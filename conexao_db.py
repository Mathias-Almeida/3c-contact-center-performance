import os

import psycopg
from dotenv import load_dotenv


# ============================================================
# CONFIGURAÇÃO
# ============================================================

# Carrega as variáveis do arquivo .env
load_dotenv()


# ============================================================
# FUNÇÃO DE CONEXÃO
# ============================================================

def obter_conexao():
    """
    Abre e retorna uma conexão com o PostgreSQL.

    As informações de acesso são obtidas
    a partir do arquivo .env.
    """

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    connection = psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )

    print("Conexão com PostgreSQL realizada com sucesso!")

    return connection


# ============================================================
# TESTE DA CONEXÃO
# ============================================================

if __name__ == "__main__":

    connection = obter_conexao()

    try:

        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM dim_date;"
        )

        quantidade = cursor.fetchone()[0]

        print(
            f"Quantidade de registros na dim_date: {quantidade}"
        )

        cursor.close()

    finally:

        connection.close()

        print("Conexão encerrada.")