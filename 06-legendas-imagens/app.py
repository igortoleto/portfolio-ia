"""Gera legendas (descrições) para imagens localmente com o modelo BLIP."""

import torch
import streamlit as st
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor

MODELO = "Salesforce/blip-image-captioning-base"


@st.cache_resource
def carregar_modelo():
    # Baixa o modelo na primeira execução (~1 GB) e reaproveita nas próximas
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    processador = BlipProcessor.from_pretrained(MODELO)
    modelo = BlipForConditionalGeneration.from_pretrained(MODELO).to(dispositivo)
    return processador, modelo, dispositivo


def gerar_legenda(imagem: Image.Image, inicio: str, num_beams: int, tamanho_max: int) -> str:
    processador, modelo, dispositivo = carregar_modelo()
    # Com "inicio" a legenda é condicionada: o modelo completa a frase
    entradas = processador(imagem, text=inicio or None, return_tensors="pt").to(dispositivo)
    with torch.no_grad():
        saida = modelo.generate(**entradas, num_beams=num_beams, max_new_tokens=tamanho_max)
    return processador.decode(saida[0], skip_special_tokens=True)


st.set_page_config(page_title="Legendas para Imagens", page_icon="🖼️")
st.title("🖼️ Legendas para Imagens")
st.write("Envie imagens e o modelo BLIP gera uma descrição para cada uma, rodando no seu computador.")

with st.sidebar:
    st.header("Configurações")
    inicio = st.text_input("Começo da legenda (opcional)", placeholder="a photography of")
    num_beams = st.slider("Beam search (qualidade x velocidade)", 1, 8, 3)
    tamanho_max = st.slider("Tamanho máximo (tokens)", 10, 60, 30)

arquivos = st.file_uploader(
    "Imagens", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True
)

if arquivos:
    with st.spinner("Carregando o modelo..."):
        carregar_modelo()

    for arquivo in arquivos:
        imagem = Image.open(arquivo).convert("RGB")
        col_img, col_texto = st.columns([1, 1])
        col_img.image(imagem, use_container_width=True)
        with col_texto:
            with st.spinner("Gerando legenda..."):
                legenda = gerar_legenda(imagem, inicio, num_beams, tamanho_max)
            st.markdown(f"**{arquivo.name}**")
            st.success(legenda)
        st.divider()
