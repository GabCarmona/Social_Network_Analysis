import nltk

print("INFO: Tentando baixar o léxico 'vader_lexicon' do NLTK...")
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
    print("INFO: 'vader_lexicon' já está baixado.")
except nltk.downloader.DownloadError:
    nltk.download('vader_lexicon')
    print("INFO: 'vader_lexicon' baixado com sucesso.")
except Exception as e:
    print(f"ERRO ao verificar/baixar 'vader_lexicon': {e}")

# Opcional, mas útil para pré-processamento de texto em geral:
print("\nINFO: Tentando baixar 'punkt' (para tokenização)...")
try:
    nltk.data.find('tokenizers/punkt')
    print("INFO: 'punkt' já está baixado.")
except nltk.downloader.DownloadError:
    nltk.download('punkt')
    print("INFO: 'punkt' baixado com sucesso.")
except Exception as e:
    print(f"ERRO ao verificar/baixar 'punkt': {e}")

print("\nINFO: Tentando baixar 'stopwords' (lista de palavras comuns)...")
try:
    nltk.data.find('corpora/stopwords')
    print("INFO: 'stopwords' já está baixado.")
except nltk.downloader.DownloadError:
    nltk.download('stopwords')
    print("INFO: 'stopwords' baixado com sucesso.")
except Exception as e:
    print(f"ERRO ao verificar/baixar 'stopwords': {e}")

print("\nDownloads do NLTK concluídos (ou recursos já existentes).")