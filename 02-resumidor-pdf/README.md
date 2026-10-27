# 📄 Resumidor de PDF

Aplicação que extrai o texto de um PDF e gera um resumo com LLM (Llama 3 via Groq). Funciona com documentos longos, como artigos, apostilas e relatórios.

## Funcionalidades

- Upload de PDF e extração de texto com `pypdf`
- Três estilos de resumo: curto, detalhado e em tópicos
- Barra de progresso e download do resumo em `.txt`

## Como funciona (map-reduce)

LLMs têm um limite de contexto, então um PDF grande não cabe em uma única chamada. A solução:

1. **Dividir**: o texto é quebrado em partes de ~12 mil caracteres, cortando em quebras de linha
2. **Map**: cada parte é resumida separadamente
3. **Reduce**: os resumos parciais são combinados em um resumo final no estilo escolhido

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # coloque sua GROQ_API_KEY
streamlit run app.py
```

## Limitações

PDFs escaneados (só imagem) não têm texto extraível. Para eles seria preciso OCR.
