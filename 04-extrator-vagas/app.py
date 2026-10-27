"""Extrai dados estruturados (JSON) de descrições de vagas de emprego com LLM."""

import json
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODELO = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

ESQUEMA = """{
  "cargo": "string",
  "empresa": "string ou null",
  "local": "string ou null",
  "modalidade": "remoto | híbrido | presencial | null",
  "senioridade": "estágio | júnior | pleno | sênior | especialista | null",
  "salario": "string ou null",
  "tecnologias": ["string"],
  "requisitos": ["string"],
  "diferenciais": ["string"],
  "beneficios": ["string"]
}"""

VAGA_EXEMPLO = """Desenvolvedor(a) Python Júnior - Tech Solutions

Local: Rio de Janeiro/RJ (modelo híbrido, 3x por semana no escritório)
Faixa salarial: R$ 4.000 a R$ 5.500

Buscamos uma pessoa desenvolvedora para atuar no time de dados.

Requisitos:
- Cursando ou formado em Ciência da Computação ou áreas afins
- Experiência com Python e SQL
- Conhecimento de Git
- Noções de APIs REST

Diferenciais:
- Experiência com FastAPI ou Django
- Conhecimento em Docker e AWS
- Inglês intermediário

Benefícios: vale-refeição, plano de saúde, auxílio home office e Gympass."""


@st.cache_resource
def criar_cliente() -> Groq:
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def extrair_dados(texto_vaga: str) -> dict:
    resposta = criar_cliente().chat.completions.create(
        model=MODELO,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você extrai informações de vagas de emprego. Responda apenas com um JSON válido "
                    f"seguindo exatamente este esquema:\n{ESQUEMA}\n"
                    "Use null ou lista vazia quando a informação não estiver no texto. Não invente dados."
                ),
            },
            {"role": "user", "content": texto_vaga},
        ],
        response_format={"type": "json_object"},  # força a saída em JSON
        temperature=0,
    )
    return json.loads(resposta.choices[0].message.content)


def mostrar_lista(titulo: str, itens: list[str]):
    if itens:
        st.markdown(f"**{titulo}**")
        st.markdown("\n".join(f"- {item}" for item in itens))


st.set_page_config(page_title="Extrator de Vagas", page_icon="🧾", layout="wide")
st.title("🧾 Extrator de Vagas")
st.write("Cole a descrição de uma vaga e a IA transforma o texto em dados estruturados.")

if not os.getenv("GROQ_API_KEY"):
    st.error("Defina GROQ_API_KEY no arquivo .env.")
    st.stop()

if "vagas" not in st.session_state:
    st.session_state.vagas = []

col_texto, col_resultado = st.columns(2)

with col_texto:
    if st.button("Usar vaga de exemplo"):
        st.session_state.texto_vaga = VAGA_EXEMPLO
    texto = st.text_area("Descrição da vaga", height=400, key="texto_vaga")
    extrair = st.button("Extrair dados", type="primary", disabled=not texto.strip())

with col_resultado:
    if extrair:
        with st.spinner("Analisando a vaga..."):
            try:
                dados = extrair_dados(texto)
            except json.JSONDecodeError:
                st.error("O modelo não retornou um JSON válido. Tente novamente.")
                st.stop()
        st.session_state.vagas.append(dados)

        st.subheader(dados.get("cargo") or "Vaga")
        c1, c2, c3 = st.columns(3)
        c1.metric("Modalidade", dados.get("modalidade") or "-")
        c2.metric("Senioridade", dados.get("senioridade") or "-")
        c3.metric("Salário", dados.get("salario") or "-")
        mostrar_lista("Tecnologias", dados.get("tecnologias", []))
        mostrar_lista("Requisitos", dados.get("requisitos", []))
        mostrar_lista("Diferenciais", dados.get("diferenciais", []))
        mostrar_lista("Benefícios", dados.get("beneficios", []))

        with st.expander("JSON gerado"):
            st.json(dados)

# Tabela com todas as vagas analisadas na sessão
if st.session_state.vagas:
    st.divider()
    st.subheader(f"Vagas analisadas ({len(st.session_state.vagas)})")
    tabela = pd.DataFrame(st.session_state.vagas)
    for coluna in ["tecnologias", "requisitos", "diferenciais", "beneficios"]:
        if coluna in tabela:
            tabela[coluna] = tabela[coluna].apply(lambda v: ", ".join(v) if isinstance(v, list) else v)
    st.dataframe(tabela, use_container_width=True)
    st.download_button("Baixar CSV", tabela.to_csv(index=False).encode("utf-8"), file_name="vagas.csv")
