"""Perguntas e respostas sobre documentos com RAG (embeddings + ChromaDB + LLM)."""

import hashlib
import os

import chromadb
import streamlit as st
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader

load_dotenv()

MODELO = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
# Modelo de embeddings multilíngue: entende português e roda localmente
MODELO_EMBEDDINGS = "paraphrase-multilingual-MiniLM-L12-v2"
PASTA_INDICE = "chroma_db"
TAMANHO_TRECHO = 800  # caracteres
SOBREPOSICAO = 150  # caracteres repetidos entre trechos vizinhos
QTD_TRECHOS = 4  # quantos trechos relevantes enviar ao modelo


@st.cache_resource
def criar_cliente() -> Groq:
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


@st.cache_resource
def abrir_colecao():
    # O índice fica salvo em disco, então os documentos não precisam ser reprocessados
    banco = chromadb.PersistentClient(path=PASTA_INDICE)
    return banco.get_or_create_collection(
        name="documentos",
        embedding_function=SentenceTransformerEmbeddingFunction(model_name=MODELO_EMBEDDINGS),
        metadata={"hnsw:space": "cosine"},
    )


def ler_arquivo(arquivo) -> str:
    if arquivo.name.lower().endswith(".pdf"):
        return "\n".join(p.extract_text() or "" for p in PdfReader(arquivo).pages)
    return arquivo.read().decode("utf-8", errors="ignore")


def dividir_em_trechos(texto: str) -> list[str]:
    passo = TAMANHO_TRECHO - SOBREPOSICAO
    trechos = (texto[inicio:inicio + TAMANHO_TRECHO].strip() for inicio in range(0, len(texto), passo))
    return [t for t in trechos if t]


def indexar(colecao, arquivo) -> int:
    """Adiciona o arquivo ao índice. Retorna quantos trechos foram criados (0 se já estava indexado)."""
    conteudo = arquivo.getvalue()
    # O hash identifica o conteúdo: o mesmo arquivo não é indexado duas vezes
    id_doc = hashlib.md5(conteudo).hexdigest()
    if colecao.get(where={"id_doc": id_doc}, limit=1)["ids"]:
        return 0

    trechos = dividir_em_trechos(ler_arquivo(arquivo))
    if trechos:
        colecao.add(
            ids=[f"{id_doc}-{i}" for i in range(len(trechos))],
            documents=trechos,
            metadatas=[{"id_doc": id_doc, "origem": arquivo.name} for _ in trechos],
        )
    return len(trechos)


def documentos_indexados(colecao) -> dict[str, str]:
    """Retorna {id_doc: nome do arquivo} de tudo que está no índice."""
    metadados = colecao.get(include=["metadatas"])["metadatas"]
    return {m["id_doc"]: m["origem"] for m in metadados}


def buscar(colecao, pergunta: str) -> list[dict]:
    if colecao.count() == 0:
        return []
    resultado = colecao.query(query_texts=[pergunta], n_results=min(QTD_TRECHOS, colecao.count()))
    return [
        # Com distância de cosseno, similaridade = 1 - distância
        {"origem": meta["origem"], "texto": doc, "score": 1 - dist}
        for doc, meta, dist in zip(
            resultado["documents"][0], resultado["metadatas"][0], resultado["distances"][0]
        )
    ]


def responder(pergunta: str, contexto: list[dict]) -> str:
    fontes = "\n\n".join(
        f"[{i}] ({t['origem']})\n{t['texto']}" for i, t in enumerate(contexto, start=1)
    )
    prompt = (
        "Responda à pergunta usando SOMENTE as fontes abaixo. Cite as fontes usadas no formato [n]. "
        "Se a resposta não estiver nas fontes, diga que não encontrou a informação.\n\n"
        f"Fontes:\n{fontes}\n\nPergunta: {pergunta}"
    )
    resposta = criar_cliente().chat.completions.create(
        model=MODELO,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    return resposta.choices[0].message.content


st.set_page_config(page_title="Perguntas sobre Documentos", page_icon="🔎")
st.title("🔎 Perguntas sobre Documentos (RAG)")
st.write("Envie seus arquivos e faça perguntas. As respostas citam os trechos usados.")

if not os.getenv("GROQ_API_KEY"):
    st.error("Defina GROQ_API_KEY no arquivo .env.")
    st.stop()

with st.spinner("Carregando o modelo de embeddings..."):
    colecao = abrir_colecao()

with st.sidebar:
    st.header("Base de documentos")
    arquivos = st.file_uploader(
        "Adicionar arquivos (.pdf, .txt, .md)", type=["pdf", "txt", "md"], accept_multiple_files=True
    )
    for arquivo in arquivos or []:
        with st.spinner(f"Indexando {arquivo.name}..."):
            novos = indexar(colecao, arquivo)
        if novos:
            st.toast(f"{arquivo.name}: {novos} trechos indexados")

    documentos = documentos_indexados(colecao)
    st.caption(f"{len(documentos)} documento(s), {colecao.count()} trechos no índice")
    for id_doc, nome in documentos.items():
        col_nome, col_botao = st.columns([4, 1])
        col_nome.write(f"📄 {nome}")
        if col_botao.button("🗑️", key=id_doc, help="Remover do índice"):
            colecao.delete(where={"id_doc": id_doc})
            st.rerun()

if colecao.count() == 0:
    st.info("Adicione pelo menos um arquivo na barra lateral para começar.")
    st.stop()

pergunta = st.text_input("Sua pergunta")
if pergunta:
    contexto = buscar(colecao, pergunta)

    with st.spinner("Gerando resposta..."):
        st.markdown(responder(pergunta, contexto))

    with st.expander("Trechos usados como contexto"):
        for i, t in enumerate(contexto, start=1):
            st.markdown(f"**[{i}] {t['origem']}** (similaridade: {t['score']:.2f})")
            st.text(t["texto"])
