# 🖼️ Legendas para Imagens

Gera descrições automáticas de imagens (*image captioning*) com o modelo **BLIP** da Salesforce, rodando **localmente** com Hugging Face Transformers e PyTorch. Não precisa de chave de API.

## Funcionalidades

- Upload de várias imagens de uma vez
- **Legenda condicionada**: você escreve o começo da frase (ex.: `a photography of`) e o modelo completa
- Ajuste de *beam search* e tamanho máximo da legenda
- Usa GPU automaticamente se houver uma disponível

## Conceitos aplicados

- **Modelo multimodal**: o BLIP combina um codificador de imagem (Vision Transformer) com um decodificador de texto
- **Inferência local**: o modelo é baixado uma vez (~1 GB) e fica em cache
- **Estratégias de decodificação**: *beam search* explora várias sequências e escolhe a mais provável
- **Cache de recursos**: `st.cache_resource` evita recarregar o modelo a cada interação

## Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

As legendas saem em inglês, que é o idioma em que o modelo foi treinado.

## Usos possíveis

Texto alternativo (acessibilidade), organização de fotos, busca de imagens por texto.
