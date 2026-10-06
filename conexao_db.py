import os
import psycopg
from dotenv import load_dotenv


# Carrega as variáveis do arquivo .env
load_dotenv()


# Dados de conexão
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")


# Conexão com PostgreSQL
connection = psycopg.connect(
    host=host,
    port=port,
    dbname=dbname,
    user=user,
    password=password
)


print("Conexão com PostgreSQL realizada com sucesso!")


# Teste simples
cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM dim_date;")

quantidade = cursor.fetchone()[0]

print(f"Quantidade de registros na dim_date: {quantidade}")


# Encerramento
cursor.close()
connection.close()

print("Conexão encerrada.")