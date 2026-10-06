import os
import psycopg
from datetime import date, timedelta
from dotenv import load_dotenv


# ==================================================
# 1. CARREGAR VARIÁVEIS DO ARQUIVO .ENV
# ==================================================

load_dotenv()


# ==================================================
# 2. CONEXÃO COM O POSTGRESQL
# ==================================================

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


# ==================================================
# 3. PERÍODO DA DIM_DATE
# ==================================================

data_inicial = date(2026, 1, 1)
data_final = date(2026, 12, 31)


# ==================================================
# 4. FERIADOS
# ==================================================

feriados = {
    date(2026, 1, 1): "Confraternização Universal",
    date(2026, 4, 21): "Tiradentes",
    date(2026, 5, 1): "Dia do Trabalho",
    date(2026, 9, 7): "Independência do Brasil",
    date(2026, 10, 12): "Nossa Senhora Aparecida",
    date(2026, 11, 2): "Finados",
    date(2026, 11, 15): "Proclamação da República",
    date(2026, 11, 20): "Dia da Consciência Negra",
    date(2026, 12, 25): "Natal"
}


# ==================================================
# 5. NOMES DOS MESES
# ==================================================

nomes_meses = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
}


# ==================================================
# 6. NOMES DOS DIAS DA SEMANA
# ==================================================

nomes_dias = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo"
}


# ==================================================
# 7. LISTA QUE VAI GUARDAR OS REGISTROS
# ==================================================

registros = []


# ==================================================
# 8. GERAR OS REGISTROS
# ==================================================

data_atual = data_inicial

while data_atual <= data_final:

    date_key = int(data_atual.strftime("%Y%m%d"))

    year = data_atual.year
    month = data_atual.month
    day_of_month = data_atual.day

    quarter = ((month - 1) // 3) + 1

    week_of_year = data_atual.isocalendar().week

    day_of_week = data_atual.weekday()

    month_name = nomes_meses[month]
    day_name = nomes_dias[day_of_week]

    is_weekend = day_of_week >= 5

    is_holiday = data_atual in feriados

    if is_holiday:
        holiday_name = feriados[data_atual]
    else:
        holiday_name = None

    is_business_day = not is_weekend and not is_holiday

    registro = (
        date_key,
        data_atual,
        year,
        quarter,
        month,
        month_name,
        week_of_year,
        day_of_month,
        day_of_week,
        day_name,
        is_weekend,
        is_holiday,
        holiday_name,
        is_business_day
    )

    registros.append(registro)

    data_atual += timedelta(days=1)


print(f"Registros preparados: {len(registros)}")


# ==================================================
# 9. INSERIR OS REGISTROS NO POSTGRESQL
# ==================================================

cursor = connection.cursor()

sql = """
    INSERT INTO dim_date (
        date_key,
        full_date,
        year,
        quarter,
        month,
        month_name,
        week_of_year,
        day_of_month,
        day_name,
        day_of_week,
        is_weekend,
        is_holiday,
        holiday_name,
        is_business_day
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s
    )
"""

cursor.executemany(sql, registros)


# ==================================================
# 10. CONFIRMAR A TRANSAÇÃO
# ==================================================

connection.commit()

print("Dados inseridos com sucesso!")


# ==================================================
# 11. VERIFICAR QUANTIDADE DE REGISTROS
# ==================================================

cursor.execute("""
    SELECT COUNT(*)
    FROM dim_date;
""")

quantidade = cursor.fetchone()[0]

print(f"Registros existentes na dim_date: {quantidade}")


# ==================================================
# 12. ENCERRAR
# ==================================================

cursor.close()
connection.close()

print("Conexão encerrada.")