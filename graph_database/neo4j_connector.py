# analise_tweets_neo4j/graph_database/neo4j_connector.py

from neo4j import GraphDatabase, exceptions
from config import settings # Importa suas configurações (URI, USER, PASSWORD)

# Variável global para armazenar o driver, se você quiser gerenciá-lo globalmente (opcional)
# _driver = None

def connect_db():
    """
    Cria e retorna uma instância do driver do Neo4j.
    """
    uri = settings.NEO4J_URI
    user = settings.NEO4J_USER
    password = settings.NEO4J_PASSWORD

    if not all([uri, user, password]):
        print("ERRO: Credenciais do Neo4j (URI, USER, PASSWORD) não estão completamente configuradas.")
        print("Verifique seu arquivo .env e config/settings.py.")
        return None

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        # Verifica a conectividade
        driver.verify_connectivity()
        print(f"INFO: Conectado com sucesso ao Neo4j em {uri}")
        return driver
    except exceptions.AuthError as e:
        print(f"ERRO DE AUTENTICAÇÃO: Não foi possível conectar ao Neo4j. Verifique usuário e senha.")
        print(f"Detalhes: {e}")
        return None
    except exceptions.ServiceUnavailable as e:
        print(f"ERRO DE SERVIÇO: Não foi possível conectar ao Neo4j em {uri}. O servidor está rodando?")
        print(f"Detalhes: {e}")
        return None
    except Exception as e:
        print(f"ERRO DESCONHECIDO ao conectar ao Neo4j: {e}")
        return None

def close_db(driver):
    """
    Fecha a conexão do driver do Neo4j.
    """
    if driver:
        try:
            driver.close()
            print("INFO: Conexão com o Neo4j fechada.")
        except Exception as e:
            print(f"ERRO ao fechar a conexão com o Neo4j: {e}")

# Bloco de teste para executar este arquivo diretamente
if __name__ == '__main__':
    print("--- Testando o conector do Neo4j ---")
    neo4j_driver = connect_db()

    if neo4j_driver:
        print("Operações com o driver poderiam ser feitas aqui (ex: executar uma query simples).")
        # Exemplo de query simples para testar (opcional):
        try:
            with neo4j_driver.session() as session:
                result = session.run("MATCH (n) RETURN count(n) AS node_count")
                record = result.single()
                if record:
                    print(f"Contagem de nós no banco: {record['node_count']}")
                else:
                    print("Não foi possível obter a contagem de nós.")
        except Exception as e_query:
            print(f"Erro ao executar query de teste: {e_query}")
        
        close_db(neo4j_driver)
    else:
        print("Não foi possível estabelecer a conexão com o Neo4j.")
    print("--- Fim do teste do conector ---")