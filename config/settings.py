# analise_tweets_neo4j/config/settings.py

import os
from dotenv import load_dotenv

# Encontra o diretório raiz do projeto para carregar o .env corretamente
# __file__ é o caminho para config/settings.py
# os.path.dirname(__file__) é config/
# os.path.dirname(os.path.dirname(__file__)) é a raiz do projeto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOTENV_PATH = os.path.join(PROJECT_ROOT, '.env')

if os.path.exists(DOTENV_PATH):
    load_dotenv(DOTENV_PATH)
else:
    print(f"AVISO: Arquivo .env não encontrado em {DOTENV_PATH}. Usando variáveis de ambiente do sistema se disponíveis.")

# Credenciais do Neo4j
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Caminho para o dataset
DATASET_FILE_PATH = os.getenv("DATASET_FILE_PATH")

# Validação simples (opcional, mas recomendado)
if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
    print("ALERTA: Credenciais do Neo4j não configuradas completamente. Verifique seu arquivo .env ou variáveis de ambiente.")

if not DATASET_FILE_PATH:
    print("ALERTA: Caminho do dataset (DATASET_FILE_PATH) não configurado. Verifique seu arquivo .env ou variáveis de ambiente.")
else:
    # Constrói o caminho absoluto para o dataset a partir da raiz do projeto
    # Isso torna o caminho mais robusto, não importa de onde os scripts são chamados.
    ABSOLUTE_DATASET_FILE_PATH = os.path.join(PROJECT_ROOT, DATASET_FILE_PATH)
    if not os.path.exists(ABSOLUTE_DATASET_FILE_PATH):
        print(f"ALERTA: Arquivo do dataset não encontrado em {ABSOLUTE_DATASET_FILE_PATH} (configurado como {DATASET_FILE_PATH}).")

# Para testar se as configurações estão sendo carregadas (opcional)
# print(f"Neo4j URI: {NEO4J_URI}")
# print(f"Dataset Path: {DATASET_FILE_PATH}")
# print(f"Absolute Dataset Path: {ABSOLUTE_DATASET_FILE_PATH if 'ABSOLUTE_DATASET_FILE_PATH' in locals() else 'Não definido'}")

# Encontra o diretório raiz do projeto para carregar o .env corretamente
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOTENV_PATH = os.path.join(PROJECT_ROOT, '.env')

print(f"DEBUG [settings.py]: Tentando carregar .env de: {DOTENV_PATH}")

if os.path.exists(DOTENV_PATH):
    load_dotenv(DOTENV_PATH)
    print(f"DEBUG [settings.py]: .env carregado.")
else:
    print(f"AVISO [settings.py]: Arquivo .env não encontrado em {DOTENV_PATH}.")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
DATASET_FILE_PATH = os.getenv("DATASET_FILE_PATH")


# Validação simples 
if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
    print("ALERTA [settings.py]: Credenciais do Neo4j não configuradas completamente.")
ABSOLUTE_DATASET_FILE_PATH = None # Inicializa para evitar erro se DATASET_FILE_PATH for None
if DATASET_FILE_PATH:
    ABSOLUTE_DATASET_FILE_PATH = os.path.join(PROJECT_ROOT, DATASET_FILE_PATH)
    if not os.path.exists(ABSOLUTE_DATASET_FILE_PATH):
        print(f"ALERTA [settings.py]: Arquivo do dataset não encontrado em {ABSOLUTE_DATASET_FILE_PATH} (configurado como {DATASET_FILE_PATH}).")
else:
    print("ALERTA [settings.py]: Caminho do dataset (DATASET_FILE_PATH) não configurado.")