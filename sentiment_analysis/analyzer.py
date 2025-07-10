# analise_tweets_neo4j/sentiment_analysis/analyzer.py

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sentiment_analysis.preprocessor import preprocess_text_for_sentiment # Importa nossa função

# Inicializa o SentimentIntensityAnalyzer uma vez para reutilização
# Isso carrega o léxico vader_lexicon que baixamos
try:
    analyzer = SentimentIntensityAnalyzer()
except LookupError as e:
    print(f"ERRO: vader_lexicon não encontrado. Por favor, execute o script de download do NLTK.")
    print(f"Detalhes: {e}")
    analyzer = None # Define como None para que as tentativas de uso falhem graciosamente

def get_vader_sentiment(text):
    """
    Analisa o sentimento de um texto usando VADER e retorna os scores.
    Retorna um dicionário com 'neg', 'neu', 'pos', 'compound'.
    """
    if analyzer is None:
        print("ERRO: SentimentIntensityAnalyzer não foi inicializado.")
        return {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0} # Retorno padrão em caso de erro

    # Pré-processa o texto antes de analisar
    processed_text = preprocess_text_for_sentiment(text)
    
    # Obtém os scores de polaridade do VADER
    # vs é um dicionário: {'neg': N, 'neu': N, 'pos': N, 'compound': N}
    #   neg: score de negatividade
    #   neu: score de neutralidade
    #   pos: score de positividade
    #   compound: score normalizado agregado, de -1 (mais extremo negativo) a +1 (mais extremo positivo)
    sentiment_scores = analyzer.polarity_scores(processed_text)
    return sentiment_scores

def classify_sentiment_from_compound_score(compound_score):
    """
    Classifica o sentimento em 'positive', 'negative', ou 'neutral'
    com base no score 'compound' do VADER.
    Limiares comuns: compound >= 0.05 para positivo, <= -0.05 para negativo.
    """
    if compound_score >= 0.05:
        return 'positive'
    elif compound_score <= -0.05:
        return 'negative'
    else:
        return 'neutral'

def analyze_sentiment_of_tweet(tweet_text):
    """
    Função completa que recebe o texto de um tweet, obtém os scores VADER,
    e classifica o sentimento.
    Retorna um dicionário com o label do sentimento e o score compound.
    """
    if not isinstance(tweet_text, str) or not tweet_text.strip():
        return {'label': 'neutral', 'score': 0.0, 'error': 'Texto vazio ou inválido'}

    vader_scores = get_vader_sentiment(tweet_text)
    compound_score = vader_scores['compound']
    sentiment_label = classify_sentiment_from_compound_score(compound_score)
    
    return {
        'label': sentiment_label,
        'score_compound': compound_score,
        'score_positive': vader_scores['pos'],
        'score_negative': vader_scores['neg'],
        'score_neutral': vader_scores['neu']
    }

if __name__ == '__main__':
    # Exemplos de teste
    tweets_de_exemplo = [
        "I LOVE this new product! It's AMAZING!!! <3 #awesome @User123 http://example.com",
        "This is the WORST experience ever... So sad. :(",
        "Just okay, not good not bad #neutral",
        "@SomeUser The movie was great, but the ending was NOT good.",
        "VADER is smart, handsome, and funny.", # Exemplo positivo do próprio VADER
        "This is a sad and pathetic attempt.",
        "I am feeling very neutral about this.",
        "The service was good, but the food was terrible." # Exemplo misto
    ]

    if analyzer: # Só executa se o analyzer foi inicializado com sucesso
        for i, tweet in enumerate(tweets_de_exemplo):
            print(f"\n--- Tweet de Exemplo {i+1} ---")
            print(f"Texto Original: '{tweet}'")
            
            # Texto pré-processado (como seria passado para VADER)
            processed_for_vader = preprocess_text_for_sentiment(tweet)
            print(f"Texto Pré-processado para VADER: '{processed_for_vader}'")
            
            # Análise de sentimento
            sentiment_result = analyze_sentiment_of_tweet(tweet) # A função interna já pré-processa
            
            print(f"Sentimento Classificado: {sentiment_result['label']}")
            print(f"Score Compound: {sentiment_result['score_compound']:.4f}") # Formata para 4 casas decimais
            print(f"  Scores Detalhados: Pos: {sentiment_result['score_positive']:.4f}, Neu: {sentiment_result['score_neutral']:.4f}, Neg: {sentiment_result['score_negative']:.4f}")
    else:
        print("\nNão foi possível executar os exemplos pois o SentimentIntensityAnalyzer não foi carregado.")