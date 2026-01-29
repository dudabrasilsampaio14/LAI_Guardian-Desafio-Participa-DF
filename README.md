🏛️ **LAI Guardian**
============================================================

**Auditoria, Classificação e Anonimização de Pedidos de Acesso à Informação com Foco em LGPD**

1º Hackathon em Controle Social – **Desafio Participa DF**  
Edital nº 10/2025 – Controladoria-Geral do Distrito Federal (CGDF)  
Categoria: **Acesso à Informação**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![LGPD](https://img.shields.io/badge/Conformidade-LGPD-green)
![Auditável](https://img.shields.io/badge/Resultado-Auditável-success)
![Pipeline](https://img.shields.io/badge/Execução-Pipeline%20Completo-blueviolet)
![Hackathon](https://img.shields.io/badge/Hackathon-Participa%20DF-orange)

---

📌 **Contexto Institucional**
------------------------------------------------------------

No âmbito da Lei de Acesso à Informação (Lei nº 12.527/2011), pedidos classificados como públicos **não podem conter dados pessoais**, sob pena de violação à Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018).

Na prática administrativa, a triagem manual desses pedidos é custosa, sujeita a erro humano e difícil de auditar posteriormente.

O **LAI Guardian** surge como uma solução automatizada de **apoio à decisão**, permitindo identificar pedidos que contenham dados pessoais, gerar versões seguras para publicação e produzir evidências técnicas para auditoria e controle.

---

🎯 **Objetivo da Solução**
------------------------------------------------------------

Apoiar equipes de transparência, ouvidoria e controle interno na análise de pedidos de acesso à informação, reduzindo riscos jurídicos relacionados à LGPD e promovendo **padronização, rastreabilidade e segurança na tomada de decisão**, sem substituir a avaliação humana.

---

✅ **Funcionalidades Principais**
------------------------------------------------------------

### 🔍 Auditoria e Classificação Automática
- Análise textual dos pedidos LAI
- Identificação de dados pessoais e sensíveis
- Diferenciação explícita entre:
  - **dados pessoais (LGPD)**
  - **identificadores administrativos** (SEI, CNJ, protocolos, números de processo)

---

### 🛡️ Anonimização com Trilha de Auditoria
- Geração de versão publicável do texto (com tarjas)
- Registro detalhado em JSON contendo:
  - tipo de dado identificado
  - valor original
  - posição no texto
  - nível de risco
  - data e hora da detecção

---

### 📊 Relatórios Institucionais
- **Excel no padrão banca / CGDF / TCU**
- Aba **Resumo Executivo**
- Aba **Auditoria Detalhada**
- Filtros automáticos e destaque por criticidade

---

### 🧠 Camadas Técnicas (Opcional)
- Treinamento de modelo estatístico leve (TF-IDF + Regressão Logística)
- Avaliação técnica automática:
  - Precisão
  - Recall
  - F1-Score
  - Matriz de confusão

---

📊 **Resultados Obtidos em Execução Real**
------------------------------------------------------------

Execução do pipeline completo com **99 pedidos** da base *AMOSTRA_e-SIC*:

| Métrica | Resultado |
|------|-----------|
| Precisão | **100%** |
| Recall (Segurança) | **100%** |
| F1-Score | **100%** |
| Falsos Negativos (FN) | **0** |

> A ausência de falsos negativos é especialmente relevante em contexto de LGPD, pois indica que nenhum pedido com dado pessoal deixou de ser identificado.

**Resumo da Auditoria:**
- Total de registros analisados: 99
- Pedidos com dados pessoais: 52 (52,53%)

---

🚀 **Execução Rápida**
------------------------------------------------------------

```bash
python run.py
O comando executa automaticamente, conforme os arquivos disponíveis:

Auditoria e classificação (Excel)

Anonimização com trilha de auditoria (JSON)

Treinamento e avaliação do modelo (opcional)

As saídas são organizadas em:

data/processed/run_YYYYMMDD_HHMMSS/
📂 Estrutura de Entrada Esperada
Auditoria de pedidos
data/raw/AMOSTRA_e-SIC.xlsx
Coluna esperada:

Texto Mascarado

Base rotulada (opcional)
data/raw/dataset_labeled.csv
🧠 Estratégia de Detecção
O LAI Guardian adota abordagem híbrida:

Regras e Validações

Regex

Validação matemática de CPF (Módulo 11)

Filtros anti-falso-positivo

PLN (opcional)

Reconhecimento de entidades (NER)

Modelo Estatístico (opcional)

Classificador leve como camada de apoio

Identificadores administrativos são tratados explicitamente para evitar classificação indevida como dado pessoal.

⚙️ Instalação
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # Linux/macOS
pip install -r requirements.txt
PLN (opcional):

pip install spacy
python -m spacy download pt_core_news_sm
