**Contexto e Fontes de Dados:**
Utilize os três conjuntos de dados em formato JSON abaixo como sua **única e exclusiva** fonte de informação.
**1. Métricas Chave:** Indicadores de desempenho extraídos do banco de dados.
```json
json_metricas
```
**2. Dados para Gráficos:** Séries temporais para análise de tendências.
  * **Gráfico 1:** Número de registros mensais (últimos 12 meses).
    ```json
    json_grafico_meses
    ```
  * **Gráfico 2:** Número de registros diários (últimos 30 dias).
    ```json
    json_grafico_dias
    ```
**3. Notícias Relevantes:** Compilado de notícias dos últimos 30 dias para contextualização.
```json
json_noticias
```
**Definição das Métricas:**
  * **Taxa de Aumento de Casos:** Variação percentual de novos casos (comparações de 30 dias com 30 dias anteriores, 7 dias com 7 dias anteriores e mensal do mês atual em relação o mês anterior).
  * **Taxa de Mortalidade:** Proporção de óbitos entre os casos com desfecho conhecido (cura ou óbito).
  * **Taxa de Ocupação de UTI:** Percentual de pacientes que necessitaram de internação em UTI.
  * **Taxa de Vacinação - Gripe:** Proporção de pacientes vacinados contra a gripe (com estado vacinal conhecido).
  * **Taxa de Vacinação - Covid-19:** Proporção de pacientes vacinados contra a Covid-19 (com estado vacinal conhecido).
**Estrutura e Instruções do Relatório de Saída:**
Gere um relatório seguindo rigorosamente esta estrutura:
**1. Resumo:**
  * Inicie com um parágrafo conciso destacando os principais achados. Qual é a situação geral da SRAG com base na correlação entre dados e notícias? Com base na análise integrada de dados e notícias, qual é a perspectiva para o futuro próximo? Destaque pontos de atenção, tendências preocupantes ou sinais positivos que merecem ser monitorados.
  * Máximo de 150 palavras
**2. Análise das Métricas Chave:**
  * Para as métricas de uma forma geral, comente objetivamente o que o significam e utilize as informações do JSON `Notícias Relevantes` para contextualizar e, se possível, explicar o porquê desses valores. (Ex: Um aumento na `increase_rate` pode ser explicado por uma notícia sobre uma nova variante em uma região específica).
    * Máximo de 120 palavras
**3. Análise de Tendências (Gráficos):**
  * Com base no JSON `Dados para Gráficos`:
      * Descreva as tendências observadas (picos, vales, períodos de estabilidade, crescimento ou queda) e correlacione essas tendências com as notícias fornecidas para explicar os padrões visuais. (Ex: Um pico de casos no gráfico pode coincidir com uma notícia sobre um grande evento ou feriado).
    * Máximo de 100 palavras
**Diretrizes e Regras:**
  * **Tom e Estilo:** Adote um tom objetivo, analítico e informativo, adequado para um briefing a gestores de saúde.
  * **Fidelidade aos Dados:** Baseie **TODAS** as suas afirmações estritamente nas informações contidas nos JSONs fornecidos.
  * **Tratamento de Incertezas:** Não invente informações. Se uma correlação direta entre os dados e as notícias não for evidente, declare isso explicitamente (ex: "Não foi encontrada uma notícia no material fornecido que justifique diretamente essa variação.").
  * **Clareza:** Evite jargões excessivos e foque em uma comunicação clara e direta.