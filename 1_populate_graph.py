# 1_populate_graph_v3.py
# NOVA VERSÃO: Lê os arquivos CSV localmente com a biblioteca pandas e envia os dados para o Neo4j.
# Esta abordagem não requer mover os arquivos para a pasta 'import' do Neo4j.

import os
import pandas as pd
from graph_database import neo4j_connector

# --- CONFIGURAÇÃO DOS ARQUIVOS ---
# Caminhos para os arquivos CSV dentro da sua pasta 'data' no projeto
TWEETS_FILE_PATH = os.path.join('data', 'tweets_neo4j_completos_FINAL.csv')
FOLLOWERS_FILE_PATH = os.path.join('data', 'seguidores_para_neo4j_simples.csv')


# Lista de queries para criar as constraints (índices de unicidade)
# Isso garante a integridade dos dados e otimiza as buscas.
CONSTRAINTS_QUERIES = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (u:Usuario) REQUIRE u.id IS UNIQUE;",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Tweet) REQUIRE t.id IS UNIQUE;",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (m:Midia) REQUIRE m.url IS UNIQUE;",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (h:Hashtag) REQUIRE h.nome IS UNIQUE;",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Assunto) REQUIRE a.nome IS UNIQUE;",
]

# --- NOVAS QUERIES PARAMETRIZADAS ---
# Estas queries recebem os dados de cada linha do CSV como um parâmetro ($row)

# CORREÇÃO: A verificação da data agora é mais específica, checando se o texto começa com um ano de 4 dígitos.
CREATE_USER_TWEET_QUERY = """
// Cria ou atualiza o usuário
MERGE (u:Usuario {id: $row.usuario_id})
  ON CREATE SET u.handle = $row.handle,
                u.criado_em = CASE WHEN $row.criado_em_usuario IS NOT NULL AND ($row.criado_em_usuario STARTS WITH '20' OR $row.criado_em_usuario STARTS WITH '19') THEN datetime(replace($row.criado_em_usuario, ' ', 'T')) ELSE null END,
                u.seguidores = toInteger($row.seguidores),
                u.regiao = $row.regiao,
                u.influente = toBoolean($row.influente)
// Cria ou atualiza o tweet
MERGE (t:Tweet {id: toInteger($row.tweet_id)})
  ON CREATE SET t.texto = $row.texto,
                t.criado_em = CASE WHEN $row.criado_em IS NOT NULL AND ($row.criado_em STARTS WITH '20' OR $row.criado_em STARTS WITH '19') THEN datetime(replace($row.criado_em, ' ', 'T')) ELSE null END,
                t.idioma = $row.idioma,
                t.likes = toInteger($row.likes)
// Cria o relacionamento e DEPOIS define as propriedades
MERGE (u)-[r:POSTA]->(t)
SET r.momento = CASE WHEN $row.momento IS NOT NULL AND ($row.momento STARTS WITH '20' OR $row.momento STARTS WITH '19') THEN datetime(replace($row.momento, ' ', 'T')) ELSE null END,
    r.dispositivo = $row.dispositivo
"""

# CORREÇÃO: Verificação de data mais específica.
CREATE_RETWEET_REL_QUERY = """
MATCH (u:Usuario {id: $row.usuario_id})
MATCH (orig:Tweet {id: toInteger($row.retweet_de_id)})
// Usa FOREACH e CASE para lidar com retweets com e sem comentário de forma condicional
FOREACH (_ IN CASE WHEN $row.comentario IS NOT NULL AND $row.comentario <> "" THEN [1] ELSE [] END |
  MERGE (u)-[r:RETWEETA]->(orig)
  SET r.momento = CASE WHEN $row.momento IS NOT NULL AND ($row.momento STARTS WITH '20' OR $row.momento STARTS WITH '19') THEN datetime(replace($row.momento, ' ', 'T')) ELSE null END,
      r.dispositivo = $row.dispositivo,
      r.comentario = $row.comentario
)
FOREACH (_ IN CASE WHEN $row.comentario IS NULL OR $row.comentario = "" THEN [1] ELSE [] END |
  MERGE (u)-[r:RETWEETA]->(orig)
  SET r.momento = CASE WHEN $row.momento IS NOT NULL AND ($row.momento STARTS WITH '20' OR $row.momento STARTS WITH '19') THEN datetime(replace($row.momento, ' ', 'T')) ELSE null END,
      r.dispositivo = $row.dispositivo
)
"""

CREATE_REPLY_REL_QUERY = """
MATCH (t:Tweet {id: toInteger($row.tweet_id)})
MATCH (orig:Tweet {id: toInteger($row.reply_to_id)})
MERGE (t)-[:REPLY_TO]->(orig)
"""

CREATE_MEDIA_REL_QUERY = """
MERGE (m:Midia {url: $row.midia_url})
  ON CREATE SET m.tipo = $row.midia_tipo,
                m.tamanho = toInteger($row.tamanho)
WITH m
MATCH (t:Tweet {id: toInteger($row.tweet_id)})
MERGE (t)-[:POSSUI_MIDIA]->(m)
"""

CREATE_HASHTAG_REL_QUERY = """
UNWIND $tags AS tag
WITH tag WHERE tag IS NOT NULL AND trim(tag) <> ""
MERGE (h:Hashtag {nome: trim(tag)})
WITH h
MATCH (t:Tweet {id: toInteger($tweet_id)})
MERGE (t)-[:POSSUI_HASHTAG]->(h)
"""

CREATE_SUBJECT_REL_QUERY = """
MERGE (a:Assunto {nome: $row.assunto_nome})
  ON CREATE SET a.tema_pai = $row.tema_pai
WITH a
MATCH (t:Tweet {id: toInteger($row.tweet_id)})
MERGE (t)-[:SOBRE]->(a)
"""

# CORREÇÃO: Verificação de data mais específica.
CREATE_FOLLOW_REL_QUERY = """
MATCH (seguidor:Usuario {id: $row.seguidor_id})
MATCH (seguido:Usuario {id: $row.seguido_id})
MERGE (seguidor)-[r:SEGUE]->(seguido)
SET r.desde = CASE WHEN $row.desde IS NOT NULL AND ($row.desde STARTS WITH '20' OR $row.desde STARTS WITH '19') THEN datetime(replace($row.desde, ' ', 'T')) ELSE null END
"""

def run_query(tx, query, params=None):
    """Função genérica para executar uma query com parâmetros."""
    tx.run(query, params)

def populate_new_model_graph():
    """
    Orquestra a carga de dados lendo os CSVs localmente e enviando os dados para o Neo4j.
    """
    print("--- FASE 1: INICIANDO CARGA COM O NOVO MODELO DE GRAFO (LEITURA LOCAL) ---")
    driver = neo4j_connector.connect_db()
    if not driver:
        return

    # Limpeza do banco de dados
    print("Limpando o banco de dados...")
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        for constraint in session.run("SHOW CONSTRAINTS"):
            try:
                session.run(f"DROP CONSTRAINT {constraint['name']}")
            except:
                pass # Ignora erros se a constraint não existir mais
    print("Banco de dados limpo.")

    with driver.session() as session:
        # 1. Criar Constraints
        print("\nPasso 1: Criando constraints...")
        for constraint in CONSTRAINTS_QUERIES:
            session.execute_write(run_query, constraint)
        print("Constraints criadas com sucesso.")

        # 2. Ler o arquivo de tweets
        print(f"\nPasso 2: Lendo arquivo de tweets de '{TWEETS_FILE_PATH}'...")
        try:
            df_tweets = pd.read_csv(TWEETS_FILE_PATH, dtype=str).fillna('')
            print(f"{len(df_tweets)} linhas carregadas do CSV de tweets.")
        except FileNotFoundError:
            print(f"ERRO: Arquivo não encontrado em '{TWEETS_FILE_PATH}'. Verifique o caminho.")
            neo4j_connector.close_db(driver)
            return

        # 3. Processar cada linha do CSV de tweets
        print("\nPasso 3: Processando tweets, usuários, mídias, hashtags e assuntos...")
        for index, row in df_tweets.iterrows():
            row_dict = row.to_dict()
            
            # Cria Usuário, Tweet e relação POSTA
            session.execute_write(run_query, CREATE_USER_TWEET_QUERY, params={'row': row_dict})
            
            # Cria relação de Retweet
            if row['tipo_interacao'] == 'RETWEETA' and row['retweet_de_id']:
                session.execute_write(run_query, CREATE_RETWEET_REL_QUERY, params={'row': row_dict})

            # Cria relação de Reply
            if row['reply_to_id']:
                session.execute_write(run_query, CREATE_REPLY_REL_QUERY, params={'row': row_dict})

            # Cria Mídia e relação
            if row['midia_url']:
                session.execute_write(run_query, CREATE_MEDIA_REL_QUERY, params={'row': row_dict})

            # Cria Hashtags e relações
            if row['hashtags_extraidas']:
                tags = row['hashtags_extraidas'].split(';')
                session.execute_write(run_query, CREATE_HASHTAG_REL_QUERY, params={'tags': tags, 'tweet_id': row['tweet_id']})
            
            # Cria Assunto e relação
            if row['assunto_nome']:
                session.execute_write(run_query, CREATE_SUBJECT_REL_QUERY, params={'row': row_dict})

            if (index + 1) % 500 == 0:
                print(f"  {index + 1}/{len(df_tweets)} tweets processados...")
        print("Processamento de tweets concluído.")

        # 4. Ler e processar o arquivo de seguidores
        print(f"\nPasso 4: Lendo e processando seguidores de '{FOLLOWERS_FILE_PATH}'...")
        try:
            df_followers = pd.read_csv(FOLLOWERS_FILE_PATH, dtype=str).fillna('')
            print(f"{len(df_followers)} relações de seguidores para criar.")
            for index, row in df_followers.iterrows():
                session.execute_write(run_query, CREATE_FOLLOW_REL_QUERY, params={'row': row.to_dict()})
            print("Processamento de seguidores concluído.")
        except FileNotFoundError:
            print(f"AVISO: Arquivo de seguidores não encontrado em '{FOLLOWERS_FILE_PATH}'. Pulando esta etapa.")

    print("\n--- CARGA COMPLETA COM O NOVO MODELO CONCLUÍDA ---")
    neo4j_connector.close_db(driver)

if __name__ == '__main__':
    # Certifique-se de ter o pandas instalado: pip install pandas
    populate_new_model_graph()
