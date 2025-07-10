# analise_tweets_neo4j/data_processing/tweet_data_mapper.py

import re
from datetime import datetime
import pandas as pd

def parse_hashtags_from_string(hashtags_string):
    """
    Converte uma string de hashtags (ex: "#tag1 #tag2") em uma lista.
    """
    if not isinstance(hashtags_string, str):
        return []
    # Remove o '#' e divide a string por espaços
    return [tag.strip() for tag in hashtags_string.replace('#', '').split() if tag.strip()]

def extract_mentions_from_text(text):
    """
    Extrai @menções do texto do tweet usando regex.
    """
    if not isinstance(text, str):
        return []
    # Regex melhorada para lidar com @ user e @user
    return list(set(re.findall(r"@\s?([a-zA-Z0-9_À-ÖØ-öø-ÿ]+)", text)))

def safe_int_conversion(value, default=0):
    if pd.isna(value):
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def safe_bool_conversion(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ['true', '1', 't', 'y', 'yes', 'verdadeiro']
    return False

def parse_datetime_string(date_string):
    if pd.isna(date_string) or not date_string:
        return None
    try:
        return pd.to_datetime(date_string).isoformat()
    except (ValueError, TypeError):
        return str(date_string)

def map_dataset_row_to_tweet_data(row_dict):
    """
    Mapeia uma linha do NOVO dataset para a estrutura de dados padronizada.
    """
    if not row_dict or not isinstance(row_dict, dict):
        return None

    tweet_text = row_dict.get('texto')
    if pd.isna(tweet_text) or not str(tweet_text).strip():
        return None

    user_id = row_dict.get('usuario_id')
    if pd.isna(user_id):
        return None

    text_mentions_usernames = extract_mentions_from_text(tweet_text)

    parsed_tweet = {
        "tweet_id": str(row_dict.get('tweet_id')),
        "text": tweet_text,
        "created_at": parse_datetime_string(row_dict.get('criado_em')),
        "source": row_dict.get('dispositivo'),
        "lang": row_dict.get('idioma'),

        "author_id": str(user_id), # Novo campo para o ID único do usuário
        "author_username": str(row_dict.get('handle', '')).lstrip('@'), # Usamos o 'handle' como username, removendo o @
        "author_location": row_dict.get('regiao'),
        "author_description": None, # Coluna não existe no novo dataset
        "author_created_at": parse_datetime_string(row_dict.get('criado_em_usuario')),
        "author_followers_count": safe_int_conversion(row_dict.get('seguidores')),
        "author_friends_count": 0, # Coluna não existe no novo dataset
        "author_favourites_count": 0, # Coluna não existe no novo dataset
        "author_is_verified": safe_bool_conversion(row_dict.get('influente')),

        "retweet_count": 0, # Coluna não existe no novo dataset
        "like_count": safe_int_conversion(row_dict.get('likes')),
        "reply_count": 0, # Coluna não existe no novo dataset
        "quote_count": 0, # Coluna não existe no novo dataset
        
        "hashtags": parse_hashtags_from_string(row_dict.get('hashtags_extraidas')),
        "mentions": [{"username": mention_username, "id": None} for mention_username in text_mentions_usernames],
        
        "is_retweet": str(row_dict.get('tipo_interacao', '')).upper() == 'RETWEETA',
        "retweet_of_id": row_dict.get('retweet_de_id'), # Novo campo
        "reply_to_id": row_dict.get('reply_to_id') # Novo campo
    }
    return parsed_tweet

# No final de tweet_data_mapper.py
if __name__ == '__main__':
    print("--- Testando o novo tweet_data_mapper.py ---")
    # Criamos um dicionário que simula uma linha do seu NOVO CSV
    sample_row_from_new_dataset = {
        'tweet_id': '500000',
        'texto': 'Learn about how you can help us solve the most pressing problems affecting our workforce. #Neo4j @Gemini',
        'criado_em': '2024-12-09',
        'idioma': 'en',
        'likes': '2521', # Testando com string
        'usuario_id': 'user_1409',
        'handle': '@user_1409',
        'criado_em_usuario': '2019-08-19',
        'seguidores': 45668,
        'regiao': 'AF',
        'influente': 'TRUE',
        'tipo_interacao': 'POSTA',
        'dispositivo': 'Android',
        'hashtags_extraidas': '#Neo4j'
        # Outras colunas podem ser omitidas para o teste
    }

    mapped_data = map_dataset_row_to_tweet_data(sample_row_from_new_dataset)

    if mapped_data:
        import json
        print("Dados mapeados com sucesso:")
        # Imprime o dicionário formatado
        print(json.dumps(mapped_data, indent=2, ensure_ascii=False))
    else:
        print("ERRO: O mapeamento da linha de exemplo falhou.")