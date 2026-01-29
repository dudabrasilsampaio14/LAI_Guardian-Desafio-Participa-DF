🛡️ LAI Guardian
Auditoria, classificação e anonimização de pedidos LAI com foco em LGPD

O LAI Guardian é uma ferramenta prática para apoiar a triagem de pedidos de acesso à informação. Ele identifica dados pessoais no texto, gera uma versão publicável (com tarjas) e entrega evidências em Excel e JSON, com rastreabilidade para auditoria.

A solução foi pensada no fluxo real de trabalho: muito texto, pouco tempo, necessidade de justificar decisões e evitar exposição indevida de informações pessoais.

✅ O que ele entrega
1) Auditoria e classificação (Excel)

Gera um relatório pronto para banca/controle, com filtros e destaque por criticidade.

Colunas principais:

Contem_Dados_Pessoais

Tipos_Detectados (CPF, TELEFONE, PROCESSO_SEI, etc.)

Risco_Max (CRÍTICO/ALTO/MÉDIO/BAIXO)

Qtd_Achados

Motivo

Versao_Publicavel

2) Anonimização com trilha de auditoria (JSON)

Para cada pedido, o JSON registra:

tipo de dado encontrado

valor original (antes da tarja)

posição no texto (span)

risco atribuído

timestamp

3) Treinamento de modelo estatístico (opcional)

Se existir um CSV rotulado, o projeto treina um classificador simples (TF-IDF + regressão logística) para atuar como camada de apoio, especialmente em casos limítrofes.

4) Avaliação técnica (opcional)

Quando há base rotulada para teste, o sistema calcula métricas técnicas (Precisão, Recall e F1-Score) e gera a matriz de confusão em JSON.

📊 Resultados obtidos na prática

Em teste real com 99 pedidos da base AMOSTRA_e-SIC, executando o pipeline completo (auditoria → anonimização → treino → avaliação), o LAI Guardian apresentou os seguintes resultados:

Indicadores de desempenho

Precisão: 100%

Recall (segurança): 100%

F1-Score: 100%

Falsos Negativos (FN): 0

A ausência de falsos negativos é especialmente relevante em contexto de LGPD, pois indica que nenhum pedido com dado pessoal deixou de ser identificado pelo sistema.

Matriz de confusão

Verdadeiros Negativos (VN): 8

Verdadeiros Positivos (VP): 14

Falsos Positivos (FP): 0

Falsos Negativos (FN): 0

Resumo executivo do relatório

Total de registros analisados: 99

Registros com dados pessoais: 52

Percentual com dados pessoais: 52,53%

Distribuição por risco:

CRÍTICO: 0

ALTO: 0

MÉDIO: 46

BAIXO: 6

(sem risco identificado): 47

Esses resultados são automaticamente consolidados na aba “Resumo Executivo” do Excel gerado pelo sistema.

🚀 Uso rápido (um comando)

Na raiz do projeto:

python run.py


Esse comando tenta rodar o pipeline completo:

Auditoria + Excel (se existir data/raw/AMOSTRA_e-SIC.xlsx)

Anonimização + JSON (idem)

Treino + avaliação (se existir data/raw/dataset_labeled.csv)

As saídas ficam organizadas em:

data/processed/run_YYYYMMDD_HHMMSS/

📂 Onde colocar os arquivos
Excel de entrada (auditoria)

Coloque em:

data/raw/AMOSTRA_e-SIC.xlsx


A coluna padrão esperada é:

Texto Mascarado

Base rotulada (treino/avaliação)

Coloque em:

data/raw/dataset_labeled.csv


Colunas mínimas:

text

label_any_pii (0/1)

O repositório já traz um exemplo com colunas adicionais (label_cpf, label_phone, etc.) para ampliar a cobertura.

🧠 Como a detecção funciona (visão honesta)

O LAI Guardian combina três camadas:

Regras e validações

Regex para padrões comuns

Validação matemática de CPF (Módulo 11)

Filtros anti-falso-positivo (ex.: telefones × processos)

PLN (opcional)

Reconhecimento de nomes de pessoas via NER (spaCy), quando disponível

Modelo estatístico (opcional)

Classificador leve atuando como “rede de segurança”

Identificadores administrativos (SEI, CNJ, protocolos) são tratados explicitamente para não serem classificados como dados pessoais por engano.

📊 Relatório Excel (padrão banca / CGDF / TCU)

O Excel gerado possui duas abas:

Resumo (executivo): totais, percentuais e distribuição por risco

Auditoria (detalhada): análise linha a linha, com cabeçalho institucional, filtros, bordas, zebra e cores por criticidade

⚙️ Instalação
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt


PLN (opcional):

pip install spacy
python -m spacy download pt_core_news_sm

🧪 Execução avançada (CLI)

Além do run.py, há um CLI com opções adicionais:

python -m lai_guardian full --help