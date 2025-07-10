# analise_tweets_neo4j/graph_database/graph_builder.py

from neo4j import GraphDatabase, exceptions

def _create_user_node(tx, user_data):
    """
    Cria ou atualiza (MERGE) um nó User.
    O identificador único do usuário agora é o 'userId'.
    """
    query = (
        "MERGE (u:User {userId: $userId}) " # << MUDANÇA AQUI
        "ON CREATE SET "
        "  u.username = $username, " # Nome de usuário agora é uma propriedade
        "  u.location = $location, "
        "  u.description = $description, "
        "  u.createdAt = $createdAt, "
        "  u.followersCount = $followersCount, "
        "  u.isVerified = $isVerified, "
        "  u.lastUpdated = timestamp() "
        "ON MATCH SET "
        "  u.username = $username, "
        "  u.location = $location, "
        "  u.followersCount = $followersCount, "
        "  u.isVerified = $isVerified, "
        "  u.lastUpdated = timestamp() "
    )
    tx.run(query,
           userId=user_data['author_id'], # << MUDANÇA AQUI
           username=user_data.get('author_username'),
           location=user_data.get('author_location'),
           description=user_data.get('author_description'),
           createdAt=user_data.get('author_created_at'),
           followersCount=user_data.get('author_followers_count'),
           isVerified=user_data.get('author_is_verified')
          )

def _create_tweet_node_and_post_relationship(tx, tweet_data):
    """
    Cria ou atualiza (MERGE) um nó Tweet e o relacionamento POSTED pelo autor.
    """
    # A query para criar o tweet em si (sem sentimento) permanece a mesma do passo anterior
    query_tweet = (
        "MERGE (t:Tweet {tweetId: $tweetId}) "
        "ON CREATE SET "
        "  t.text = $text, t.createdAt = $createdAt, t.source = $source, "
        "  t.lang = $lang, t.retweetCount = $retweetCount, t.likeCount = $likeCount, "
        "  t.replyCount = $replyCount, t.quoteCount = $quoteCount, t.isRetweet = $isRetweet, "
        "  t.lastUpdated = timestamp() "
        "ON MATCH SET t.retweetCount = $retweetCount, t.likeCount = $likeCount"
    )
    tx.run(query_tweet,
           tweetId=tweet_data['tweet_id'], text=tweet_data['text'],
           createdAt=tweet_data.get('created_at'), source=tweet_data.get('source'),
           lang=tweet_data.get('lang'), retweetCount=tweet_data.get('retweet_count'),
           likeCount=tweet_data.get('like_count'), replyCount=tweet_data.get('reply_count'),
           quoteCount=tweet_data.get('quote_count'), isRetweet=tweet_data.get('is_retweet')
          )

    # Criar o relacionamento :POSTED usando o novo ID do autor
    query_posted_rel = (
        "MATCH (u:User {userId: $authorId}) " # << MUDANÇA AQUI
        "MATCH (t:Tweet {tweetId: $tweetId}) "
        "MERGE (u)-[r:POSTED]->(t)"
    )
    tx.run(query_posted_rel, authorId=tweet_data['author_id'], tweetId=tweet_data['tweet_id']) # << MUDANÇA AQUI

def _create_hashtags_and_relationships(tx, tweet_id, hashtags_list):
    # Esta função não precisa de mudanças
    if not hashtags_list: return
    query = (
        "MATCH (t:Tweet {tweetId: $tweetId}) "
        "UNWIND $tags AS tagName "
        "MERGE (h:Hashtag {tag: toLower(tagName)}) "
        "MERGE (t)-[r:HAS_TAG]->(h)"
    )
    tx.run(query, tweetId=tweet_id, tags=hashtags_list)

def _create_mentions_and_relationships(tx, tweet_id, mentions_list):
    # Esta função não precisa de mudanças na sua lógica principal,
    # mas o MERGE de User agora cria nós baseados em 'username' pois não temos o 'userId' da pessoa mencionada.
    if not mentions_list: return
    query = (
        "MATCH (t:Tweet {tweetId: $tweetId}) "
        "UNWIND $mentionedUsers AS mentionedUserData "
        # Nota: Estamos criando/encontrando usuários mencionados pelo seu username,
        # pois não temos o userId deles no texto do tweet.
        "MERGE (mentioned_u:User {username: mentionedUserData.username}) "
        "ON CREATE SET mentioned_u.isMentionOnly = true "
        "MERGE (t)-[r:MENTIONS]->(mentioned_u)"
    )
    usernames_to_merge = [{'username': mention['username']} for mention in mentions_list if mention.get('username')]
    if usernames_to_merge:
        tx.run(query, tweetId=tweet_id, mentionedUsers=usernames_to_merge)

def add_tweet_to_graph(driver, tweet_data):
    # Esta função principal não precisa de mudanças
    if not driver or not tweet_data: return
    try:
        with driver.session(database="neo4j") as session:
            session.execute_write(_create_user_node, tweet_data)
            session.execute_write(_create_tweet_node_and_post_relationship, tweet_data)
            if tweet_data.get('hashtags'):
                session.execute_write(_create_hashtags_and_relationships, tweet_data['tweet_id'], tweet_data['hashtags'])
            if tweet_data.get('mentions'):
                session.execute_write(_create_mentions_and_relationships, tweet_data['tweet_id'], tweet_data['mentions'])
    except exceptions.Neo4jError as e:
        print(f"ERRO Neo4j [graph_builder] ao processar tweet ID {tweet_data.get('tweet_id', 'DESCONHECIDO')}: {e}")
    except Exception as e:
        print(f"ERRO GERAL [graph_builder] ao processar tweet ID {tweet_data.get('tweet_id', 'DESCONHECIDO')}: {e}")
