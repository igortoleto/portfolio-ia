# 🧾 Extrator de Vagas

Transforma o texto livre de uma vaga de emprego em **dados estruturados** (JSON) usando LLM e compara a vaga com o seu currículo, gerando uma **nota de compatibilidade**.

## Funcionalidades

### 📋 Extrair dados
- Extração de cargo, modalidade, senioridade, salário, tecnologias, requisitos, diferenciais e benefícios
- Tabela com todas as vagas analisadas na sessão
- Exportação para CSV, útil para comparar várias vagas

### 🎯 Compatibilidade com currículo
- Currículo em PDF ou colado como texto
- Nota de 0 a 100, com resumo da avaliação
- Pontos fortes, lacunas e sugestões do que estudar ou destacar

Os dois modos têm exemplos prontos (vaga e currículo) para testar rápido.

## Conceitos aplicados

- **Saída estruturada**: o *JSON mode* da API (`response_format={"type": "json_object"}`) garante que a resposta seja um JSON válido
- **Esquema no prompt**: o system prompt define os campos e os valores permitidos
- **LLM como avaliador**: o modelo recebe um papel (recrutador técnico) e critérios explícitos (requisitos pesam mais que diferenciais)
- **Menos alucinação**: `temperature=0` e a instrução de não supor dados que não estão no texto
- **Validação da saída**: a nota é limitada entre 0 e 100 antes de ser exibida
- **Dados não estruturados para tabela**: JSON → pandas DataFrame → CSV

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # coloque sua GROQ_API_KEY
streamlit run app.py
```
