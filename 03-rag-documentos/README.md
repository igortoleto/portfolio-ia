# 🔎 Perguntas sobre Documentos (RAG)

Sistema de **RAG (Retrieval-Augmented Generation)**: você envia arquivos, faz perguntas e o LLM responde com base apenas no conteúdo deles, citando as fontes.

## Funcionalidades

- Upload de vários arquivos `.pdf`, `.txt` e `.md`
- **Busca semântica**: encontra trechos pelo significado, não só por palavras iguais ("salário" encontra "remuneração")
- **Índice persistente** no ChromaDB: os documentos continuam disponíveis depois de fechar o app
- Gerenciamento da base: lista de documentos indexados e botão para remover
- Respostas com citações no formato `[1]`, `[2]`...
- Painel mostrando os trechos usados e a similaridade de cada um
- O modelo avisa quando a resposta não está nos documentos (menos alucinação)

## Como funciona

```
Indexação:  documento → trechos de 800 caracteres (com sobreposição) → embeddings → ChromaDB
Consulta:   pergunta → embedding → 4 trechos mais próximos (cosseno) → prompt com contexto → LLM → resposta
```

1. **Chunking**: os textos são divididos em trechos sobrepostos para não cortar ideias no meio
2. **Embeddings**: cada trecho vira um vetor com o modelo `paraphrase-multilingual-MiniLM-L12-v2` (roda localmente e entende português)
3. **Banco vetorial**: os vetores ficam no ChromaDB, salvos na pasta `chroma_db/`
4. **Recuperação**: a pergunta também vira vetor, e o ChromaDB devolve os trechos mais próximos
5. **Geração**: os trechos vão no prompt e o modelo responde só com base neles

Cada arquivo é identificado pelo hash MD5 do conteúdo, então enviar o mesmo arquivo de novo não duplica o índice.

## Evolução do projeto

| Versão | Recuperação | Índice |
|--------|-------------|--------|
| v1 | TF-IDF (palavras em comum) | Em memória, refeito a cada execução |
| v2 | Embeddings semânticos | ChromaDB persistente |

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # coloque sua GROQ_API_KEY
streamlit run app.py
```

Na primeira execução, o modelo de embeddings (~470 MB) é baixado automaticamente.
