import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

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

nomes = [
    "Carlos", "Juliana", "Rafael", "Camila", "André",
    "Mariana", "Lucas", "Fernanda", "Bruno", "Patrícia",
    "Gustavo", "Renata", "Diego", "Larissa", "Marcelo",
    "Aline", "Thiago", "Priscila", "Eduardo", "Vanessa",
    "Rodrigo", "Beatriz", "Felipe", "Amanda", "Daniel",
    "Carolina", "Leonardo", "Natália", "Vinícius", "Bianca",
    "Gabriel", "Isabela", "Mateus", "Letícia", "Henrique",
    "Débora", "Fábio", "Raquel", "Murilo", "Cristina"
]

sobrenomes = [
    "Mendes", "Ferreira", "Martins", "Oliveira", "Carvalho",
    "Costa", "Almeida", "Santos", "Rocha", "Lima",
    "Nascimento", "Alves", "Barbosa", "Ribeiro", "Gomes",
    "Monteiro", "Castro", "Araújo", "Freitas", "Araújo",
    "Pereira", "Souza", "Silva", "Moreira", "Cardoso",
    "Teixeira", "Correia", "Moura", "Barros", "Nascimento"
]

supervisores = []

numero = 1

for nome in nomes:
    for sobrenome in sobrenomes:

        if numero > 220:
            break

        supervisor_code = f"SUP{numero:03d}"

        supervisor_name = f"{nome} {sobrenome}"

        supervisor_email = (
            f"sup{numero:03d}@3ccontactcenter.com.br"
        )

        registro = (
            supervisor_code,
            supervisor_name,
            supervisor_email,
            True,
            "2026-01-01"
        )

        supervisores.append(registro)

        numero += 1

    if numero > 220:
        break

print(f"Supervisores preparados: {len(supervisores)}")

cursor = connection.cursor()

sql = """
    INSERT INTO dim_supervisor (
        supervisor_code,
        supervisor_name,
        supervisor_email,
        is_active,
        created_date
    )
    VALUES (
        %s, %s, %s, %s, %s
    );
"""

cursor.executemany(sql, supervisores)

connection.commit()

print("Dados inseridos com sucesso!")

cursor.execute("""
    SELECT COUNT(*)
    FROM dim_supervisor;
""")

quantidade = cursor.fetchone()[0]

print(f"Registros existentes na dim_supervisor: {quantidade}")

cursor.close()
connection.close()

print("Conexão encerrada.")