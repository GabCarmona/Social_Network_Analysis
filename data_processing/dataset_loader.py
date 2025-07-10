# analise_tweets_neo4j/data_processing/dataset_loader.py

import pandas as pd
from config import settings # Importa as configurações (que incluem o caminho absoluto)
import os

def load_tweets_from_file():
    """
    Carrega tweets de um arquivo de dataset (ex: CSV) especificado nas configurações.
    Usa o caminho absoluto definido em settings.py.
    """
    # O settings.py já calcula o ABSOLUTE_DATASET_FILE_PATH
    # Se não, você pode recalcular aqui:
    # project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Navega três níveis acima se settings não fizesse
    # full_dataset_path = os.path.join(project_root, settings.DATASET_FILE_PATH)
    
    # Usando o caminho absoluto pré-calculado em settings.py para robustez
    full_dataset_path = settings.ABSOLUTE_DATASET_FILE_PATH

    if not full_dataset_path or not os.path.exists(full_dataset_path):
        print(f"ERRO: Arquivo do dataset não encontrado ou caminho não configurado. Verificado: '{full_dataset_path}'")
        print("Por favor, verifique a variável DATASET_FILE_PATH no seu arquivo .env e certifique-se de que o arquivo existe.")
        return None

    print(f"INFO: Carregando dataset de: {full_dataset_path}")
    try:
        # Tenta com UTF-8 primeiro, que é comum
        # Adiciona low_memory=False se houver problemas com tipos de dados mistos em colunas grandes
        df = pd.read_csv(full_dataset_path, encoding='utf-8', low_memory=False)
        print("INFO: Dataset carregado com sucesso usando UTF-8.")
    except UnicodeDecodeError:
        print("AVISO: Falha ao decodificar com UTF-8. Tentando com latin1...")
        try:
            df = pd.read_csv(full_dataset_path, encoding='latin1', low_memory=False)
            print("INFO: Dataset carregado com sucesso usando latin1.")
        except Exception as e_latin1:
            print(f"ERRO: Não foi possível carregar o dataset de {full_dataset_path} com latin1. Erro: {e_latin1}")
            return None
    except FileNotFoundError: # Embora já verificado, é bom ter como fallback
        print(f"ERRO: Arquivo do dataset não encontrado em {full_dataset_path}.")
        return None
    except Exception as e_general:
        print(f"ERRO: Ocorreu um problema ao carregar o dataset {full_dataset_path}. Erro: {e_general}")
        return None
    
    # Retorna uma lista de dicionários, onde cada dicionário representa uma linha do CSV
    # Isso facilita o processamento iterativo posterior
    # Se o dataset for MUITO grande, considere processar em chunks ou retornar o DataFrame
    # e iterar com df.iterrows() ou df.itertuples() no main.py
    # Por agora, converter para dicts é bom para datasets de tamanho moderado.
    if df.empty:
        print("AVISO: O dataset carregado está vazio.")
        return []
        
    return df.to_dict('records')

if __name__ == '__main__':
    # Este bloco é para testar o carregador diretamente
    print("--- Testando o dataset_loader.py ---")
    # Para que settings funcione corretamente aqui, precisamos garantir que o .env seja carregado
    # O import de 'config.settings' no topo já deve ter feito isso se o __init__.py estiver certo
    # e o .env estiver na raiz correta em relação a este script quando executado com -m
    
    tweets_data = load_tweets_from_file()
    if tweets_data is not None: # Checa se não é None (erro no carregamento)
        if tweets_data: # Checa se a lista não está vazia
            print(f"\nINFO: Carregados {len(tweets_data)} registros do dataset.")
            print("INFO: Exemplo do primeiro registro (dicionário):")
            print(tweets_data[0])
            # Para ver as colunas do DataFrame antes de converter para dict
            # df_test = pd.DataFrame(tweets_data) # Recriar df para inspecionar
            # print("\nINFO: Colunas do dataset:", df_test.columns.tolist())
            # print("\nINFO: Primeiras 5 linhas do DataFrame:")
            # print(df_test.head())
        else:
            print("INFO: O dataset foi carregado, mas está vazio.")
    else:
        print("INFO: Nenhum dado carregado devido a um erro anterior.")
    print("--- Fim do teste do dataset_loader.py ---")