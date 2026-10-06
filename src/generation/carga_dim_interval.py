import os
from datetime import time

import psycopg
from dotenv import load_dotenv


# ============================================================
# 1. Carregar as variáveis de ambiente
# ============================================================

load_dotenv()


# ============================================================
# 2. Dados de conexão
# ============================================================

host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")


# ============================================================
# 3. Conectar ao PostgreSQL
# ============================================================

connection = psycopg.connect(
    host=host,
    port=port,
    dbname=dbname,
    user=user,
    password=password
)

print("Conexão com PostgreSQL realizada com sucesso!")


# ============================================================
# 4. Gerar os 48 intervalos de 30 minutos
# ============================================================

intervalos = []

for minuto_total in range(0, 24 * 60, 30):

    # Horário inicial
    hora = minuto_total // 60
    minuto = minuto_total % 60

    inicio = time(hora, minuto)

    # Horário final
    proximo_minuto = minuto_total + 30

    if proximo_minuto == 24 * 60:
        fim = time(0, 0)
    else:
        hora_fim = proximo_minuto // 60
        minuto_fim = proximo_minuto % 60

        fim = time(hora_fim, minuto_fim)

    # Identificador do intervalo
    interval_key = (minuto_total // 30) + 1

    # Texto amigável
    interval_label = (
        f"{inicio.strftime('%H:%M')} - "
        f"{fim.strftime('%H:%M')}"
    )

    # Hora e minuto do início
    hour = hora
    minute = minuto

    registro = (
        interval_key,
        inicio,
        fim,
        interval_label,
        hour,
        minute
    )

    intervalos.append(registro)


print(f"Intervalos preparados: {len(intervalos)}")


# ============================================================
# 5. Inserir os dados no PostgreSQL
# ============================================================

cursor = connection.cursor()

sql = """
    INSERT INTO dim_interval (
        interval_key,
        start_time,
        end_time,
        interval_label,
        hour,
        minute
    )
    VALUES (
        %s, %s, %s, %s, %s, %s
    );
"""

cursor.executemany(sql, intervalos)

connection.commit()

print("Dados inseridos com sucesso!")


# ============================================================
# 6. Verificar quantidade de registros
# ============================================================

cursor.execute("""
    SELECT COUNT(*)
    FROM dim_interval;
""")

quantidade = cursor.fetchone()[0]

print(
    f"Registros existentes na dim_interval: {quantidade}"
)


# ============================================================
# 7. Encerrar conexão
# ============================================================

cursor.close()
connection.close()

print("Conexão encerrada.")