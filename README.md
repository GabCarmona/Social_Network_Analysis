# Análise de Sentimentos em Tweets com Python e Neo4j

Este projeto implementa um pipeline para processar tweets de datasets públicos, realizar análise de sentimentos e armazenar os dados e seus relacionamentos em um banco de dados orientado a grafos Neo4j, permitindo análises complexas sobre a opinião pública.

<p align="center">
  <img width="487" height="516" alt="image" src="https://github.com/user-attachments/assets/649daebc-ba9d-47a3-9376-9d2f778ed053" />
</p>


## Funcionalidades Implementadas

* **Carregamento de Dados:** Leitura de tweets a partir de arquivos de dataset locais (CSV).
* **Mapeamento de Dados:** Um "adaptador" (`tweet_data_mapper.py`) que transforma os dados brutos de diferentes formatos de CSV em uma estrutura Python padronizada e robusta.
* **Pré-processamento de Texto:** Limpeza básica do texto dos tweets para otimizar a análise de sentimento.
* **Análise de Sentimentos:**
    * Utilização da biblioteca NLTK com o léxico VADER para análise de sentimentos de tweets em inglês.
    * Classificação dos tweets como positivos, negativos ou neutros, com base em um score de sentimento composto.
* **Construção do Grafo no Neo4j:**
    * Criação de Nós: :Usuario, :Tweet, :Hashtag, :Midia (para imagens/vídeos), :Assunto.
    * Estabelecimento de relacionamentos: [:POSTA], [:RETWEETA], [:REPLY_TO], [:SEGUE], [:POSSUI_HASHTAG], [:POSSUI_MIDIA], [:SOBRE].
* **Pipeline de Duas Etapas:**
    1.  **Ingestão:** Script responsável por limpar o banco de dados, criar as constraints de unicidade e popular o grafo com todos os nós e relacionamentos estruturais a partir dos arquivos CSV.
    2.  **Enriquecimento:** Após a criação do grafo base, este script consulta os tweets (em lotes, por intervalo de ID), realiza a análise de sentimento usando a biblioteca NLTK com o léxico VADER e atualiza os nós :Tweet com as novas informações (rótulo e score de sentimento).
* **Consulta de Dados:** Script de exemplo para consultar os dados enriquecidos diretamente do Neo4j.

## Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Manipulação de Dados:** Pandas
* **Análise de Sentimentos:** NLTK (com léxico VADER para inglês)
* **Banco de Dados:** Neo4j (Banco de Dados Orientado a Grafos)
* **Driver Neo4j para Python:** `neo4j`
* **Gerenciamento de Configurações:** `python-dotenv`
* **Ambiente Virtual:** `venv`

## Configuração do Ambiente

1.  **Pré-requisitos:**
    * Python 3.7 ou superior.
    * Neo4j Desktop instalado e um banco de dados ativo, OU uma instância do Neo4j AuraDB.

2.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/GabCarmona/Social_Network_Analysis.git](https://github.com/GabCarmona/Social_Network_Analysis.git)
    cd analise_tweets_neo4j
    ```

3.  **Crie e Ative o Ambiente Virtual:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

4.  **Configure as Variáveis de Ambiente:**
    * Crie um arquivo chamado `.env` na raiz do projeto.
    * Adicione as seguintes variáveis com seus respectivos valores:
        ```ini
        # Credenciais do Neo4j
        NEO4J_URI="bolt://localhost:7687"
        NEO4J_USER="neo4j"
        NEO4J_PASSWORD=SUA_SENHA_AQUI

        # Caminho para o arquivo do dataset
        DATASET_FILE_PATH="data/tweets_neo4j_completos_FINAL.csv"
        ```

5.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

6.  **Baixe os Recursos do NLTK (para VADER):**
    ```bash
    python -c "import nltk; nltk.download('vader_lexicon');"
    ```

## Como Usar

O projeto opera em um fluxo de múltiplas etapas, separando a carga dos dados da análise.

### Passo 1: Preparar o Ambiente

* Coloque os seus arquivos `.csv` na pasta `data/`.
* Certifique-se de que o nome do arquivo corresponde ao valor de `DATASET_FILE_PATH` no seu arquivo `.env`.
* Inicie sua instância do Neo4j e certifique-se de que as credenciais no `.env` estão corretas.
* (Opcional, mas recomendado para uma nova carga) Limpe o banco de dados no Neo4j Browser: `MATCH (n) DETACH DELETE n`.

### Passo 2: Executar o Pipeline

1.  **Popular o Grafo (Carga Inicial):**
    Este script lê os arquivos CSV de entrada e cria a estrutura base do grafo, incluindo os nós :Usuario, :Tweet, :Hashtag, :Midia e :Assunto, bem como seus relacionamentos (:POSTA, :SEGUE, :RETWEETA, etc.). Esta fase é executada sem a inclusão dos dados de sentimento, que são adicionados posteriormente pelo segundo script.
    ```bash
    python 1_populate_graph.py
    ```
    *Aguarde a conclusão. Para datasets grandes, isso pode levar alguns minutos.*

2.  **Analisar Sentimentos e Atualizar o Grafo:**
    Este script busca os tweets que acabaram de ser inseridos, analisa o sentimento de cada um e **atualiza** os nós `:Tweet` com as novas propriedades de sentimento.
    ```bash
    python 2_analyze_and_update_sentiments.py
    ```
    *Este script pode ser adaptado para analisar o banco inteiro, ou apenas um intervalo específico de IDs de tweet.*

### Passo 3: Consultar e Explorar os Resultados

1.  **Explorar no Neo4j Browser:**
    * Acesse seu Neo4j Browser (geralmente `http://localhost:7474`).
    * Execute queries Cypher para visualizar e analisar o grafo. Exemplos:
        * **Contar tweets por sentimento:**
            ```cypher
            MATCH (original:Tweet {id: 509000})
            MATCH (resposta:Tweet)-[:REPLY_TO]->(original)
            WHERE resposta.sentimentLabel IS NOT NULL
            RETURN 
               resposta.sentimentLabel AS Sentimento,
              count(resposta) AS Quantidade_de_Respostas
            ```
        * **Visualizar schema:**
            ```cypher
            CALL db.schema.visualization()

            ```

---
