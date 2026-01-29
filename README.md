🛡️ LAI Guardian
============================================================

**Proteção ativa de dados pessoais em pedidos de acesso à informação**

1º Hackathon em Controle Social – Desafio Participa DF  
Edital nº 10/2025 – Controladoria-Geral do Distrito Federal (CGDF)  
Categoria: Acesso à Informação

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![LGPD](https://img.shields.io/badge/LGPD-Aplicada-success)
![Auditoria](https://img.shields.io/badge/Auditoria-Rastreável-blueviolet)
![Excel](https://img.shields.io/badge/Relatório-Excel%20Institucional-green)
![Pipeline](https://img.shields.io/badge/Execução-Um%20Comando-orange)

---

## 📍 Visão Geral

O **LAI Guardian** é uma ferramenta desenvolvida para apoiar o tratamento de pedidos de acesso à informação que possam conter **dados pessoais**, oferecendo um mecanismo automatizado de **auditoria, classificação e anonimização**, com foco na **redução de risco LGPD**.

A solução atua como um **guardião preventivo** do processo de transparência, ajudando o órgão a identificar situações sensíveis antes da publicação, sem comprometer o direito de acesso à informação.

---

## 🧭 Problema Enfrentado

Na rotina administrativa, pedidos LAI frequentemente incluem:
- dados pessoais do solicitante
- informações de terceiros
- números de documentos, contatos e endereços
- referências administrativas que podem gerar ambiguidade

A análise manual desses pedidos é demorada, difícil de padronizar e pouco auditável.

O LAI Guardian foi criado para **organizar esse processo**, fornecendo subsídios técnicos claros para a decisão final.

---

## 🎯 Finalidade da Solução

Fornecer um **apoio técnico confiável** para equipes responsáveis pela transparência pública, permitindo:

- reduzir a exposição indevida de dados pessoais
- padronizar critérios de análise
- registrar evidências para auditoria
- acelerar o fluxo de resposta aos pedidos

Sempre respeitando o papel decisório do servidor público.

---

## ⚙️ O que o LAI Guardian faz

### 🔎 Análise e Classificação
- Varre automaticamente o texto do pedido
- Identifica dados pessoais e sensíveis
- Reconhece padrões administrativos (SEI, CNJ, protocolos)
- Evita classificações equivocadas por contexto

---

### 🛡️ Anonimização Controlada
- Gera uma versão segura do texto, pronta para publicação
- Aplica tarjas apenas onde necessário
- Mantém o conteúdo informacional preservado

---

### 🧾 Trilha de Auditoria
- Cada achado é registrado em JSON com:
  - tipo de dado
  - posição no texto
  - nível de risco
  - data e hora
- Permite reavaliação posterior da decisão

---

### 📊 Relatórios para Gestão e Controle
- Excel estruturado para leitura institucional
- Aba de **Resumo Executivo**
- Aba de **Auditoria Detalhada**
- Filtros, destaques visuais e organização por risco

---

## 📈 Resultados em Ambiente de Teste

Execução do pipeline completo sobre **99 pedidos** da base *AMOSTRA_e-SIC*:

| Indicador | Resultado |
|---------|-----------|
| Precisão | 100% |
| Recall (Segurança) | 100% |
| F1-Score | 100% |
| Falsos Negativos | 0 |

**Visão geral da auditoria:**
- 52 pedidos com dados pessoais (52,53%)
- Predominância de risco médio
- Nenhum caso crítico não identificado

Esses dados são consolidados automaticamente no relatório Excel.

---

## ▶️ Execução Simplificada

Todo o fluxo pode ser executado com um único comando:

```bash
python run.py
Dependendo dos arquivos disponíveis, o sistema executa:

auditoria dos pedidos

anonimização com trilha

treinamento e avaliação do modelo (opcional)

Os resultados são organizados em:

data/processed/run_YYYYMMDD_HHMMSS/
📂 Estrutura Esperada
Entrada principal (auditoria)
data/raw/AMOSTRA_e-SIC.xlsx
Coluna esperada:

Texto Mascarado

Base rotulada (opcional)
data/raw/dataset_labeled.csv
🧠 Abordagem Técnica (resumo)
O LAI Guardian combina:

regras e validações formais

filtros contextuais

processamento de linguagem natural (opcional)

modelo estatístico leve como apoio

Identificadores administrativos são tratados separadamente para evitar falso enquadramento como dado pessoal.

🏁 Considerações Finais
O projeto foi desenvolvido com foco em aplicabilidade real, priorizando clareza, segurança jurídica e facilidade de uso, alinhado às diretrizes do Desafio Participa DF.
