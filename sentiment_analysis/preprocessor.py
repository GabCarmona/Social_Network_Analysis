# analise_tweets_neo4j/sentiment_analysis/preprocessor.py
import re
# from nltk.tokenize import word_tokenize # Poderia ser usado para tokenização mais avançada
# from nltk.corpus import stopwords # Poderia ser usado para remover stopwords
# import string

# stop_words_en = set(stopwords.words('english')) if 'stopwords' in nltk.corpus.util.available_corpora else set()

def preprocess_text_for_sentiment(text):
    """
    Realiza uma limpeza básica no texto para análise de sentimento com VADER.
    VADER é sensível a maiúsculas e pontuação para intensidade, então algumas
    limpezas padrão (como lowercasing total ou remoção de pontuação)
    devem ser feitas com cuidado ou omitidas.
    """
    if not isinstance(text, str):
        return ""

    # 1. Remover URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # 2. Remover menções de usuário (@username) - geralmente não contribuem para o sentimento do texto em si.
    #    VADER não tem scores para nomes de usuário.
    text = re.sub(r'@\w+', '', text)
    
    # 3. Remover hashtags (o símbolo '#') mas manter a palavra da tag.
    #    VADER pode ter scores para palavras que são comumente usadas como hashtags.
    #    Ex: '#खुश' (Hindi para feliz) tem score no léxico VADER. #happy também.
    #    Alternativamente, poderia remover a hashtag inteira: re.sub(r'#\w+', '', text)
    # text = text.replace('#', '') # Remove apenas o símbolo '#'
    
    # 4. Remover caracteres especiais (exceto pontuação que VADER usa, como '!' ou '?')
    #    Esta etapa é opcional e pode ser muito agressiva para VADER.
    #    VADER lida bem com muita "bagunça" de mídias sociais.
    #    text = re.sub(r'[^A-Za-z0-9\s.!?]', '', text) # Exemplo, mantém letras, números, espaços e .!?

    # 5. Remover espaços extras
    text = " ".join(text.split())

    # 6. Lowercasing (CAUTELA com VADER):
    #    VADER usa MAIÚSCULAS para indicar intensidade (ex: "GREAT" é mais positivo que "great").
    #    Se converter para minúsculas, essa informação de intensidade é perdida.
    #    Para uma análise mais simples ou se não se importar com essa nuance, pode descomentar:
    #    text = text.lower()

    # 7. Remoção de Stopwords (CAUTELA com VADER):
    #    VADER é projetado para funcionar bem com stopwords, pois algumas (como "not") invertem o sentimento.
    #    Geralmente não é recomendado remover stopwords antes de usar VADER.
    #    Se quisesse:
    #    if stop_words_en: # Verifica se a lista de stopwords foi carregada
    #        word_tokens = word_tokenize(text)
    #        filtered_text = [w for w in word_tokens if not w.lower() in stop_words_en]
    #        text = " ".join(filtered_text)
            
    return text.strip()

if __name__ == '__main__':
    sample_tweet1 = "I LOVE this new product! It's AMAZING!!! <3 #awesome @User123 http://example.com"
    sample_tweet2 = "This is the WORST experience ever... So sad. :("
    sample_tweet3 = "Just okay, not good not bad #neutral"
    sample_tweet4 = "@SomeUser The movie was great, but the ending was NOT good." # Teste de negação

    print(f"Original: '{sample_tweet1}'")
    print(f"Preprocessed: '{preprocess_text_for_sentiment(sample_tweet1)}'\n")

    print(f"Original: '{sample_tweet2}'")
    print(f"Preprocessed: '{preprocess_text_for_sentiment(sample_tweet2)}'\n")

    print(f"Original: '{sample_tweet3}'")
    print(f"Preprocessed: '{preprocess_text_for_sentiment(sample_tweet3)}'\n")
    
    print(f"Original: '{sample_tweet4}'")
    print(f"Preprocessed: '{preprocess_text_for_sentiment(sample_tweet4)}'\n")