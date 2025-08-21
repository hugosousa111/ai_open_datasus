# Análise de Dados da SRAG

## Sobre o Projeto

Este projeto consiste em um pipeline de dados automatizado para coletar, processar, analisar e visualizar dados de **Síndrome Respiratória Aguda Grave (SRAG)** do Brasil, provenientes do sistema OpenDATASUS.

O objetivo principal é criar um fluxo robusto e modular que transforma dados brutos em insights, gerando um relatório. A arquitetura é baseada em **agentes AI**, onde cada agente é responsável por uma etapa específica do pipeline, como download de dados, pré-processamento, cálculo de métricas e geração de relatórios.

---

## Explicação em Vídeo
Acesse o vídeo com a explicação geral do projeto ([Vídeo Explicação](https://youtu.be/qFmbjXlOhGw))

---

## Funcionalidades Principais

-   **Pipeline Automatizado:** Execução de todo o fluxo de dados com um único comando.
-   **Arquitetura Baseada em Agentes:** Lógica modularizada em agentes para cada tarefa (download, processamento, etc.).
-   **Coleta de Notícias:** Integração com API de notícias para contextualizar os dados com eventos atuais.
-   **Geração de Métricas e Visualizações:** Criação automática de gráficos e métricas relevantes.
-   **Geração de Relatórios:** Produção de relatório final em formatos em HTML e PDF.

---

## Como Executar

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### Pré-requisitos

-   Python 3.9+
-   Git

### 1. Clonar o Repositório

```bash
git clone https://github.com/hugosousa111/ai_open_datasus.git
cd ai_open_datasus
```

### 2. Configurar o Ambiente Virtual

É uma boa prática usar um ambiente virtual para isolar as dependências do projeto.

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar o ambiente
# No Windows
venv\Scripts\activate
# No macOS/Linux
source venv/bin/activate
```

*Observação: Quando quiser desativar o ambiente virtual, basta executar o comando `deactivate` no seu terminal.*

### 3. Instalar as Dependências

As dependências do projeto estão listadas no arquivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo `.env.example` para um novo arquivo chamado `.env` e preencha com suas chaves de API e outras configurações necessárias.

```bash
copy .env.example .env
```

Agora, edite o arquivo `.env` com suas informações. Atualize os valores das chaves para o SERPER e para o OPENAI.

### 5. Executar o Pipeline

Para iniciar o pipeline completo, execute o script principal:

```bash
python src/main.py
```

Isso irá acionar a sequência de agentes para executar todas as etapas do projeto.

### (Opcional) Desenvolvimento com Jupyter Lab

Se você precisar trabalhar com os notebooks do projeto, pode iniciar o Jupyter Lab.

```bash
jupyter lab
```

---

## Estrutura do Projeto


```
.
├── conf/               # Arquivos de configuração (parâmetros, e os templates do prompt e relatorio.html).
├── data/               # Dados do projeto, separados por estágios do pipeline.
│   ├── 01_raw/           # Dados brutos e imutáveis (notebooks).
│   ├── 02_intermediate/  # Dados intermediários, como o dicionário (notebooks). 
│   ├── 03_final/         # Datasets finais, prontos para análise  (notebooks).
│   ├── 04_raw_auto/      # Dados brutos baixados automaticamente.
│   ├── 05_final_auto/    # Datasets finais gerados automaticamente.
│   ├── 06_metrics/       # Métricas calculadas.
│   ├── 07_visualizations/# Gráficos gerados.
│   ├── 08_news/          # Notícias relacionadas coletadas.
│   ├── 09_report/        # Relatório AI em Markdown.
│   └── 10_final_report/  # Relatório final em HTML.
├── logs/               # Arquivos de log da aplicação.
├── notebooks/          # Notebooks para exploração.
├── src/                # Código-fonte principal da aplicação.
│   ├── agents/           # Agentes responsáveis por orquestrar as tarefas.
│   ├── tools/            # Ferramentas (tools) executadas pelos agentes.
│       └── try_news/     # Teste de ferramentas de notícias.
│   ├── utils/            # Funções utilitárias.
│   └── graph.py          # Graph Workflow do langgraph
│   └── main.py           # Ponto de entrada para execução do pipeline.
│   └── old_main.py       # Ponto de entrada para execução do pipeline (sem langgraph).
├── .env.example        # Arquivo de exemplo para variáveis de ambiente.
├── requirements.txt    # Lista de dependências Python.
└── README.md           # Documentação do projeto.
```

---

## Diagrama Conceitual

Para acessar o diagrama dos agentes desse projeto, clique em: [Diagrama Conceitual (PDF)](./DiagramaConceitual.pdf).


-----

## Decisões de Projeto

Esta seção documenta algumas decisões técnicas tomadas durante o desenvolvimento do projeto.

### Geração de PDF

Para a funcionalidade de geração de relatórios em PDF:

**Bibliotecas Testadas:**

  * **WeasyPrint:** Exige a instalação de dependências externas ao ecossistema Python.
  * **PDFKit:** Similar ao WeasyPrint, requer a instalação do `wkhtmltopdf`, uma dependência externa.
  * **xhtml2pdf:** Apresentou dificuldades na formatação do layout do PDF.
  * **Playwright:** Exige a instalação de dependências externas ao ecossistema Python.

A biblioteca **ReportLab** foi a escolhida. Exigindo algumas alterações na estrutura do HTML de template do relatório. 

### Coleta de Notícias

Bibliotecas foram testadas com parâmetros de busca equivalentes.

**APIs e Bibliotecas Avaliadas:**

  * **gnews:** Retornou um volume alto de artigos (100), apresentou lentidão durante a pesquisa.
  * **newsapi-python:** Encontrou 11 artigos e o conteúdo era restrito a apenas 200 caracteres.
  * **Google Serper:** Apresentou 6 artigos e também com uma prévia de 200 caracteres do conteúdo.

Foi decidido utilizar o **Google Serper integrado através da `langchain_community`**.

### Linter e Formatador de Código

O **Ruff** foi adotado como ferramenta de linting e formatação.

**Como Executar:**

1.  Para formatar o código em todo o projeto:

    ```bash
    ruff format .
    ```

2.  Para verificar e corrigir automaticamente os erros de linting:

    ```bash
    ruff check . --fix
    ```

## Tratamento e Limpeza dos Dados

As seguintes etapas de pré-processamento foram aplicadas:

### 1. Simplificação da Variável `EVOLUCAO`
- Para simplificar a análise os valores da categoria "Óbito por outras causas" foram unificados com a categoria "Óbito".

### 2. Mapeamento de Categorias
- Todas as variáveis que utilizavam códigos numéricos para representar categorias foram mapeadas para seus nomes correspondentes.

### 3. Tratamento de Dados Ausentes
- Os valores ausentes (`NaN`) em todas as colunas foram substituídos pela categoria "Ignorado", permitindo que essas observações fossem mantidas na análise sem gerar erros.
- Amostras com datas ausentes (`NaN`) são excluidas (caso não encontrado ainda)

## Análise de Métricas e Visualizações

Este projeto contém dois componentes principais para a análise dos dados de saúde: um para o **cálculo de métricas** e outro para a **geração de visualizações**.

---

### Módulo de Métricas

Este módulo é responsável por calcular métricas epidemiológicas a partir dos dados processados. Ele analisa os dados em diferentes janelas de tempo (últimos 7 dias, últimos 30 dias e mês corrente) para fornecer um panorama da situação atual e sua evolução.

As métricas calculadas são:

* **Taxa de Aumento de Casos (%):** Compara o número total de casos notificados em um período recente (ex: últimos 7 dias) com o período imediatamente anterior de mesma duração. Um valor positivo indica aceleração no número de casos, enquanto um negativo indica desaceleração.
    * **Fórmula:** $((\text{Casos}_{\text{período atual}} - \text{Casos}_{\text{período anterior}}) / \text{Casos}_{\text{período anterior}}) \times 100$

* **Taxa de Mortalidade (%):** Indica a proporção de casos notificados (com evolução definida como "Cura" ou "Óbito") que resultaram em morte dentro de um determinado período. É um indicador da letalidade da doença entre os casos reportados.
    * **Fórmula:** $((\text{Total de Óbitos}) / (\text{Total de Casos com Evolução Definida})) \times 100$

* **Taxa de Ocupação de UTI (%):** Mede a porcentagem de pacientes notificados que necessitaram de internação em Unidade de Terapia Intensiva (UTI). Este valor reflete a gravidade dos casos e a pressão sobre o sistema de saúde.
    * **Fórmula:** $((\text{Total de Casos em UTI}) / (\text{Total de Casos com Status de UTI Definido})) \times 100$

* **Taxa de Vacinação (Gripe e COVID-19) (%):** Calcula, separadamente para gripe (`VACINA`) e COVID-19 (`VACINA_COV`), a porcentagem de pessoas com casos notificados que já haviam sido vacinadas.

#### Saídas Geradas

Ao final da execução, este módulo salva os seguintes arquivos no formato JSON:
* `metrics.json`: Contém os valores calculados para todas as métricas mencionadas, organizadas por período.
* `periods.json`: Detalha as datas de início e fim exatas para cada período analisado (ex: "last_7_days").

---

### Módulo de Visualizações

Este módulo foca em traduzir os dados numéricos em gráficos intuitivos, facilitando a identificação de tendências e padrões ao longo do tempo.

Os gráficos e dados gerados são:

* **1. Análise Diária dos Últimos 30 Dias**
    * **Gráfico (Linha):** `last_30_days.png`
        * Mostra a evolução diária do número de novos casos notificados. É ideal para visualizar picos recentes, vales e a tendência de curto prazo (se os casos estão subindo, caindo ou estáveis).
    * **Dados (JSON):** `last_30_days.json`
        * Arquivo contendo os dados brutos que alimentam o gráfico de linha, com a contagem de casos para cada dia.

* **2. Análise Mensal dos Últimos 12 Meses**
    * **Gráfico (Barras):** `last_12_months.png`
        * Apresenta o total de casos consolidados por mês ao longo do último ano. Este gráfico é perfeito para identificar padrões de sazonalidade e tendências de longo prazo.
    * **Dados (JSON):** `last_12_months.json`
        * Arquivo com os dados agregados que alimentam o gráfico de barras, com a contagem total de casos para cada mês.