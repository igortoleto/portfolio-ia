"""Chatbot com personas usando a API da Groq (Llama 3)."""

import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODELO = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

PERSONAS = {
    "Assistente geral": "Você é um assistente prestativo. Responda em português, de forma clara e objetiva.",
    "Professor de programação": (
        "Você é um professor de programação paciente. Explique conceitos passo a passo, "
        "com exemplos de código curtos. Responda em português."
    ),
    "Recrutador técnico": (
        "Você é um recrutador técnico conduzindo uma entrevista simulada. Faça uma pergunta por vez, "
        "avalie a resposta do candidato e dê feedback construtivo. Responda em português."
    ),
    "Revisor de textos": (
        "Você é um revisor de textos. Corrija gramática e clareza do texto enviado, "
        "mostre a versão corrigida e liste as principais mudanças. Responda em português."
    ),
}


@st.cache_resource
def criar_cliente() -> Groq:
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


st.set_page_config(page_title="Chatbot Assistente", page_icon="💬")
st.title("💬 Chatbot Assistente")

with st.sidebar:
    st.header("Configurações")
    persona = st.selectbox("Persona", list(PERSONAS.keys()))
    temperatura = st.slider("Criatividade (temperature)", 0.0, 1.5, 0.7, 0.1)
    if st.button("Limpar conversa"):
        st.session_state.mensagens = []

if not os.getenv("GROQ_API_KEY"):
    st.error("Defina GROQ_API_KEY no arquivo .env para usar o chat.")
    st.stop()

# Se o usuário trocar de persona, a conversa recomeça
if st.session_state.get("persona") != persona:
    st.session_state.persona = persona
    st.session_state.mensagens = []

for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if pergunta := st.chat_input("Digite sua mensagem..."):
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    historico = [{"role": "system", "content": PERSONAS[persona]}] + st.session_state.mensagens

    with st.chat_message("assistant"):
        stream = criar_cliente().chat.completions.create(
            model=MODELO,
            messages=historico,
            temperature=temperatura,
            stream=True,
        )
        # Mostra a resposta conforme ela é gerada
        resposta = st.write_stream(
            chunk.choices[0].delta.content or "" for chunk in stream
        )

    st.session_state.mensagens.append({"role": "assistant", "content": resposta})
