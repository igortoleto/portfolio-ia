# 🎨 Gerador de Imagens

Gera imagens a partir de descrições em texto (*text-to-image*) usando modelos de difusão hospedados no Hugging Face: **FLUX.1 schnell** e **Stable Diffusion XL**.

## Funcionalidades

- Escolha do modelo e do tamanho da imagem
- Estilos prontos (fotografia, aquarela, pixel art...) adicionados ao prompt
- Galeria com as imagens geradas na sessão
- Download em PNG

## Conceitos aplicados

- **Modelos de difusão**: partem de ruído aleatório e "limpam" a imagem aos poucos, guiados pelo texto
- **Engenharia de prompt**: modificadores de estilo mudam bastante o resultado
- **Inferência remota**: o modelo roda nos servidores do Hugging Face, então não é preciso GPU local

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # coloque seu HF_TOKEN
streamlit run app.py
```

O token gratuito do Hugging Face tem uma cota mensal de uso. Se aparecer erro de limite, espere ou troque de modelo.
