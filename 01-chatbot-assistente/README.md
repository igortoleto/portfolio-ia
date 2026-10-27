# 💬 Chatbot Assistente

Chatbot com interface web que conversa usando um LLM (Llama 3 via Groq). Você escolhe uma **persona** (assistente geral, professor de programação, recrutador técnico ou revisor de textos) e o modelo adapta o comportamento.

## Funcionalidades

- Histórico da conversa mantido durante a sessão
- Respostas em **streaming** (aparecem enquanto são geradas)
- Personas definidas por *system prompt*
- Controle de criatividade (`temperature`)

## Conceitos aplicados

- **System prompt**: define o papel e o tom do modelo
- **Contexto de conversa**: todo o histórico é enviado a cada chamada, porque o modelo não guarda memória sozinho
- **Streaming**: consome a resposta token a token

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # coloque sua GROQ_API_KEY
streamlit run app.py
```
