"""Resumidor de PDFs com LLM usando a estratégia map-reduce."""

import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader

load_dotenv()

MODELO = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
TAMANHO_PARTE = 12_000  # caracteres por parte enviada ao modelo

ESTILOS = {
    "Curto": "um resumo curto de no máximo 1 parágrafo",
    "Detalhado": "um resumo detalhado com os principais argumentos e conclusões",
    "Tópicos": "um resumo em tópicos (bullet points) com as ideias principais",
}


@st.cache_resource
def criar_cliente() -> Groq:
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def extrair_texto(arquivo) -> str:
    leitor = PdfReader(arquivo)
    return "\n".join(pagina.extract_text() or "" for pagina in leitor.pages)


def dividir_texto(texto: str, tamanho: int) -> list[str]:
    """Divide o texto em partes, tentando cortar em quebras de parágrafo."""
    partes = []
    while len(texto) > tamanho:
        corte = texto.rfind("\n", 0, tamanho)
        if corte < tamanho // 2:
            corte = tamanho
        partes.append(texto[:corte])
        texto = texto[corte:]
    if texto.strip():
        partes.append(texto)
    return partes


def chamar_llm(prompt: str) -> str:
    resposta = criar_cliente().chat.completions.create(
        model=MODELO,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return resposta.choices[0].message.content


def resumir(texto: str, estilo: str, progresso) -> str:
    partes = dividir_texto(texto, TAMANHO_PARTE)

    # Etapa "map": resume cada parte separadamente
    resumos_parciais = []
    for i, parte in enumerate(partes, start=1):
        progresso.progress(i / (len(partes) + 1), text=f"Resumindo parte {i} de {len(partes)}...")
        resumos_parciais.append(
            chamar_llm(f"Resuma em português os pontos principais deste trecho:\n\n{parte}")
        )

    # Etapa "reduce": junta os resumos parciais no resumo final
    progresso.progress(1.0, text="Gerando resumo final...")
    juntos = "\n\n".join(resumos_parciais)
    return chamar_llm(
        f"A partir dos resumos parciais abaixo, escreva em português {ESTILOS[estilo]} "
        f"do documento completo.\n\n{juntos}"
    )


st.set_page_config(page_title="Resumidor de PDF", page_icon="📄")
st.title("📄 Resumidor de PDF")
st.write("Envie um PDF e receba um resumo gerado por IA.")

if not os.getenv("GROQ_API_KEY"):
    st.error("Defina GROQ_API_KEY no arquivo .env.")
    st.stop()

arquivo = st.file_uploader("Arquivo PDF", type="pdf")
estilo = st.radio("Estilo do resumo", list(ESTILOS.keys()), horizontal=True)

if arquivo and st.button("Resumir", type="primary"):
    texto = extrair_texto(arquivo)
    if not texto.strip():
        st.warning("Não foi possível extrair texto. O PDF pode ser escaneado (imagem).")
        st.stop()

    st.caption(f"{len(texto):,} caracteres extraídos".replace(",", "."))
    barra = st.progress(0.0)
    resumo = resumir(texto, estilo, barra)
    barra.empty()

    st.subheader("Resumo")
    st.markdown(resumo)
    st.download_button("Baixar resumo (.txt)", resumo, file_name="resumo.txt")
