"""Gerador de imagens a partir de texto usando modelos de difusão (Hugging Face)."""

import io
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

MODELOS = {
    "FLUX.1 schnell (rápido)": "black-forest-labs/FLUX.1-schnell",
    "Stable Diffusion XL": "stabilityai/stable-diffusion-xl-base-1.0",
}

ESTILOS = {
    "Nenhum": "",
    "Fotografia": ", fotografia realista, alta resolução, iluminação natural",
    "Ilustração digital": ", ilustração digital, cores vibrantes, detalhada",
    "Aquarela": ", pintura em aquarela, traços suaves",
    "Pixel art": ", pixel art, 16 bits, estilo retrô",
    "Anime": ", estilo anime, cel shading",
}


@st.cache_resource
def criar_cliente() -> InferenceClient:
    return InferenceClient(token=os.getenv("HF_TOKEN"))


def imagem_para_bytes(imagem) -> bytes:
    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    return buffer.getvalue()


st.set_page_config(page_title="Gerador de Imagens", page_icon="🎨")
st.title("🎨 Gerador de Imagens")
st.write("Descreva uma imagem e um modelo de difusão vai criá-la.")

if not os.getenv("HF_TOKEN"):
    st.error("Defina HF_TOKEN no arquivo .env.")
    st.stop()

if "galeria" not in st.session_state:
    st.session_state.galeria = []

with st.sidebar:
    st.header("Configurações")
    nome_modelo = st.selectbox("Modelo", list(MODELOS.keys()))
    estilo = st.selectbox("Estilo", list(ESTILOS.keys()))
    largura = st.select_slider("Largura", [512, 768, 1024], value=768)
    altura = st.select_slider("Altura", [512, 768, 1024], value=768)

prompt = st.text_area("Descrição (funciona melhor em inglês)", placeholder="a cat astronaut floating in space")

if st.button("Gerar imagem", type="primary", disabled=not prompt.strip()):
    prompt_final = prompt + ESTILOS[estilo]
    with st.spinner("Gerando imagem... (a primeira vez pode demorar)"):
        try:
            imagem = criar_cliente().text_to_image(
                prompt_final, model=MODELOS[nome_modelo], width=largura, height=altura
            )
        except Exception as erro:
            st.error(f"Não foi possível gerar a imagem: {erro}")
            st.stop()
    st.session_state.galeria.insert(0, {"prompt": prompt_final, "imagem": imagem_para_bytes(imagem)})

if st.session_state.galeria:
    atual = st.session_state.galeria[0]
    st.image(atual["imagem"], caption=atual["prompt"])
    st.download_button(
        "Baixar PNG",
        atual["imagem"],
        file_name=f"imagem_{datetime.now():%Y%m%d_%H%M%S}.png",
        mime="image/png",
    )

    if len(st.session_state.galeria) > 1:
        st.subheader("Geradas anteriormente")
        colunas = st.columns(3)
        for i, item in enumerate(st.session_state.galeria[1:]):
            colunas[i % 3].image(item["imagem"], caption=item["prompt"])
