# 🧾 Extrator de Vagas

Transforma o texto livre de uma vaga de emprego em **dados estruturados** (JSON) usando LLM. Mostra cargo, modalidade, senioridade, salário, tecnologias, requisitos, diferenciais e benefícios.

## Funcionalidades

- Extração para um esquema JSON fixo
- Vaga de exemplo para testar rápido
- Tabela com todas as vagas analisadas na sessão
- Exportação para CSV, útil para comparar várias vagas

## Conceitos aplicados

- **Saída estruturada**: o *JSON mode* da API (`response_format={"type": "json_object"}`) garante que a resposta seja um JSON válido
- **Esquema no prompt**: o system prompt define os campos e os valores permitidos
- **Menos alucinação**: `temperature=0` e a instrução de usar `null` quando o dado não existe
- **Dados não estruturados para tabela**: JSON → pandas DataFrame → CSV

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # coloque sua GROQ_API_KEY
streamlit run app.py
```
