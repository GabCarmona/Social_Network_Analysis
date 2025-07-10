# 2_analyze_and_update_sentiments_v2.py
# VERSÃO ATUALIZADA para funcionar com o novo modelo de grafo.

from graph_database import neo4j_connector
from sentiment_analysis import analyzer as sentiment_analyzer

def fetch_tweets_by_id_range(driver, start_id, end_id):
    """
    Busca tweets do Neo4j cujo ID (agora numérico) esteja dentro de um intervalo.
    """
    print(f"Buscando tweets com ID no intervalo de {start_id} a {end_id} para análise...")
    
    # MUDANÇA PRINCIPAL:
    # - O MATCH agora é em 't.id' em vez de 't.tweetId'.
    # - Não precisamos mais de toInteger(), pois o ID já é um número.
    query = """
    MATCH (t:Tweet)
    WHERE t.id >= $start_id AND t.id <= $end_id
    // Opcional: Adicione esta linha para analisar apenas tweets que AINDA não têm sentimento
    // AND t.sentimentLabel IS NULL
    RETURN t.id AS tweetId, t.texto AS text
    """
    
    with driver.session() as session:
        result = session.run(query, start_id=start_id, end_id=end_id)
        return result.data()

def update_tweet_sentiment_in_db(tx, tweet_id, sentiment_data):
    """
    Atualiza um nó Tweet com as propriedades de sentimento.
    """
    # MUDANÇA PRINCIPAL:
    # - O MATCH agora é em 't.id' em vez de 't.tweetId'.
    query = """
    MATCH (t:Tweet {id: $tweetId})
    SET t.sentimentLabel = $label,
        t.sentimentScore = $score
    """
    tx.run(query, 
           tweetId=tweet_id, 
           label=sentiment_data['label'], 
           score=sentiment_data['score_compound'])

def analyze_and_update_sentiments_by_range(start_id, end_id):
    """
    Orquestra o processo de enriquecimento para um intervalo específico de IDs.
    """
    print(f"\n--- FASE 2: ANÁLISE DE SENTIMENTOS PARA TWEETS NO INTERVALO DE ID {start_id} a {end_id} ---")

    driver = neo4j_connector.connect_db()
    if not driver:
        return

    tweets_to_process = fetch_tweets_by_id_range(driver, start_id, end_id)
    
    if not tweets_to_process:
        print("Nenhum tweet encontrado neste intervalo de IDs. Processo concluído.")
        neo4j_connector.close_db(driver)
        return

    total_in_batch = len(tweets_to_process)
    print(f"\n{total_in_batch} tweets encontrados. Iniciando análise e atualização...")

    for i, tweet in enumerate(tweets_to_process):
        # Os nomes das chaves retornadas pela query mudaram para 'tweetId' e 'text'
        tweet_id = tweet['tweetId']
        tweet_text = tweet['text']

        sentiment_result = sentiment_analyzer.analyze_sentiment_of_tweet(tweet_text)

        try:
            with driver.session() as session:
                session.execute_write(update_tweet_sentiment_in_db, tweet_id, sentiment_result)
            if (i + 1) % 50 == 0 or (i + 1) == total_in_batch:
                print(f"  {i + 1}/{total_in_batch} tweets do lote atualizados...")
        except Exception as e:
            print(f"ERRO ao atualizar tweet ID {tweet_id}: {e}")
    
    print(f"\n--- ANÁLISE POR INTERVALO CONCLUÍDA ---")
    neo4j_connector.close_db(driver)

if __name__ == '__main__':
    # --- DEFINA AQUI O SEU INTERVALO DE IDs ---
    id_inicial = 509002
    id_final = 509401
    # ----------------------------------------
    
    analyze_and_update_sentiments_by_range(id_inicial, id_final)
