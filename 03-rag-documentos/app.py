"""Perguntas e respostas sobre documentos com RAG (busca TF-IDF + LLM)."""

import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

MODELO = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
TAMANHO_TRECHO = 800  # caracteres
SOBREPOSICAO = 150  # caracteres repetidos entre trechos vizinhos
QTD_TRECHOS = 4  # quantos trechos relevantes enviar ao modelo


@st.cache_resource
def criar_cliente() -> Groq:
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def ler_arquivo(arquivo) -> str:
    if arquivo.name.lower().endswith(".pdf"):
        return "\n".join(p.extract_text() or "" for p in PdfReader(arquivo).pages)
    return arquivo.read().decode("utf-8", errors="ignore")


def dividir_em_trechos(texto: str, origem: str) -> list[dict]:
    trechos = []
    passo = TAMANHO_TRECHO - SOBREPOSICAO
    for inicio in range(0, len(texto), passo):
        conteudo = texto[inicio:inicio + TAMANHO_TRECHO].strip()
        if conteudo:
            trechos.append({"origem": origem, "texto": conteudo})
    return trechos


def indexar(trechos: list[dict]):
    vetorizador = TfidfVectorizer()
    matriz = vetorizador.fit_transform(t["texto"] for t in trechos)
    return vetorizador, matriz


def buscar(pergunta: str, trechos, vetorizador, matriz) -> list[dict]:
    similaridades = cosine_similarity(vetorizador.transform([pergunta]), matriz)[0]
    melhores = similaridades.argsort()[::-1][:QTD_TRECHOS]
    return [trechos[i] | {"score": float(similaridades[i])} for i in melhores if similaridades[i] > 0]


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

arquivos = st.file_uploader("Arquivos (.pdf, .txt, .md)", type=["pdf", "txt", "md"], accept_multiple_files=True)

if not arquivos:
    st.info("Envie pelo menos um arquivo para começar.")
    st.stop()

trechos = [t for arq in arquivos for t in dividir_em_trechos(ler_arquivo(arq), arq.name)]
if not trechos:
    st.warning("Nenhum texto foi extraído dos arquivos.")
    st.stop()

vetorizador, matriz = indexar(trechos)
st.caption(f"{len(arquivos)} arquivo(s) indexado(s) em {len(trechos)} trechos.")

pergunta = st.text_input("Sua pergunta")
if pergunta:
    contexto = buscar(pergunta, trechos, vetorizador, matriz)
    if not contexto:
        st.warning("Nenhum trecho relacionado à pergunta foi encontrado.")
        st.stop()

    with st.spinner("Gerando resposta..."):
        st.markdown(responder(pergunta, contexto))

    with st.expander("Trechos usados como contexto"):
        for i, t in enumerate(contexto, start=1):
            st.markdown(f"**[{i}] {t['origem']}** (similaridade: {t['score']:.2f})")
            st.text(t["texto"])
