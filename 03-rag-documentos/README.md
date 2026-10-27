# 🔎 Perguntas sobre Documentos (RAG)

Sistema de **RAG (Retrieval-Augmented Generation)**: você envia arquivos, faz perguntas e o LLM responde com base apenas no conteúdo deles, citando as fontes.

## Funcionalidades

- Upload de vários arquivos `.pdf`, `.txt` e `.md`
- Respostas com citações no formato `[1]`, `[2]`...
- Painel mostrando os trechos usados e a similaridade de cada um
- O modelo avisa quando a resposta não está nos documentos (menos alucinação)

## Como funciona

```
Documentos → trechos de 800 caracteres (com sobreposição) → índice TF-IDF
Pergunta → busca dos 4 trechos mais similares (cosseno) → prompt com contexto → LLM → resposta
```

1. **Chunking**: os textos são divididos em trechos sobrepostos para não cortar ideias no meio
2. **Indexação**: cada trecho vira um vetor TF-IDF (scikit-learn)
3. **Recuperação**: a pergunta é vetorizada e comparada aos trechos por similaridade de cosseno
4. **Geração**: os trechos mais relevantes vão no prompt e o modelo responde só com base neles

## Próximos passos

- Trocar TF-IDF por *embeddings* semânticos (ex.: `sentence-transformers`)
- Guardar o índice em um banco vetorial (ex.: ChromaDB)

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # coloque sua GROQ_API_KEY
streamlit run app.py
```
