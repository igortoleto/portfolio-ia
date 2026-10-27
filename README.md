# Portfólio de IA Generativa

Coleção de projetos práticos com IA generativa: modelos de linguagem (LLMs), RAG, saída estruturada, geração de imagens e visão computacional.

Todos os projetos usam **Python** e **Streamlit** para a interface. Os que usam LLM rodam com a API da **Groq** (modelos Llama), que tem plano gratuito.

| # | Projeto | O que faz | Tecnologias |
|---|---------|-----------|-------------|
| 1 | [Chatbot Assistente](01-chatbot-assistente) | Chat com personas configuráveis, histórico e respostas em streaming | Groq, Llama 3, Streamlit |
| 2 | [Resumidor de PDF](02-resumidor-pdf) | Resume PDFs longos dividindo em partes (map-reduce) | Groq, pypdf |
| 3 | [Perguntas sobre Documentos (RAG)](03-rag-documentos) | Responde perguntas com base nos seus arquivos, citando os trechos | RAG, TF-IDF, scikit-learn, Groq |
| 4 | [Extrator de Vagas](04-extrator-vagas) | Transforma o texto de uma vaga em JSON estruturado | Groq (JSON mode), pandas |
| 5 | [Gerador de Imagens](05-gerador-imagens) | Gera imagens a partir de texto com modelos de difusão | Hugging Face Inference, FLUX / Stable Diffusion |
| 6 | [Legendas para Imagens](06-legendas-imagens) | Descreve imagens automaticamente, rodando localmente | Transformers, BLIP, PyTorch |

## Como rodar qualquer projeto

```bash
cd 01-chatbot-assistente
python -m venv .venv
# Windows: .venv\Scripts\activate | Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # e coloque sua chave
streamlit run app.py
```

## Chaves de API

- **Groq** (projetos 1 a 4): crie uma chave gratuita em https://console.groq.com/keys
- **Hugging Face** (projeto 5): crie um token gratuito em https://huggingface.co/settings/tokens
- O projeto 6 roda 100% local, sem chave.

As chaves ficam no arquivo `.env` de cada projeto, que é ignorado pelo Git.
