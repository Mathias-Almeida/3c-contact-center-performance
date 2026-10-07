import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

import pandas as pd

from conexao_db import obter_conexao
from gerar_fact_demand import gerar_fact_demand


print("=" * 50)
print("CARGA DA FACT_DEMAND")
print("=" * 50)


conexao = obter_conexao()

try:

    # ========================================================
    # 1. DATAS
    # ========================================================

    df_datas = pd.read_sql(
        """
        SELECT
            date_key,
            full_date,
            is_holiday
        FROM dim_date
        ORDER BY full_date;
        """,
        conexao
    )

    print(
        f"Datas encontradas: {len(df_datas)}"
    )


    # ========================================================
    # 2. INTERVALOS
    # ========================================================

    df_intervals = pd.read_sql(
        """
        SELECT
            interval_key,
            start_time,
            end_time
        FROM dim_interval
        ORDER BY interval_key;
        """,
        conexao
    )

    print(
        f"Intervalos encontrados: {len(df_intervals)}"
    )


    # ========================================================
    # 3. SKILLS
    # ========================================================

    df_skills = pd.read_sql(
        """
        SELECT
            skill_key,
            skill_code,
            skill_name
        FROM dim_skill
        WHERE is_active = TRUE
        ORDER BY skill_key;
        """,
        conexao
    )

    print(
        f"Skills encontradas: {len(df_skills)}"
    )


    # ========================================================
    # 4. GERA DEMANDA
    # ========================================================

    print()
    print("Gerando demanda...")

    df_demand = gerar_fact_demand(
        df_datas=df_datas,
        df_intervals=df_intervals,
        df_skills=df_skills
    )

    print(
        f"Registros gerados: {len(df_demand)}"
    )


    # ========================================================
    # 5. VALIDAÇÃO BÁSICA
    # ========================================================

    if df_demand.empty:

        raise ValueError(
            "Nenhum registro de demanda foi gerado."
        )


    colunas_obrigatorias = [
        "date_key",
        "interval_key",
        "skill_key",
        "volume_offered",
        "volume_answered",
        "volume_abandoned",
        "aht_seconds",
        "workload_seconds",
        "asa_seconds",
        "sla_target",
        "service_level",
        "created_date"
    ]

    colunas_faltantes = [
        coluna
        for coluna in colunas_obrigatorias
        if coluna not in df_demand.columns
    ]

    if colunas_faltantes:

        raise ValueError(
            "Colunas ausentes: "
            + ", ".join(colunas_faltantes)
        )


    # ========================================================
    # 6. INSERT
    # ========================================================

    cursor = conexao.cursor()

    sql_insert = """
        INSERT INTO fact_demand (
            date_key,
            interval_key,
            skill_key,
            volume_offered,
            volume_answered,
            volume_abandoned,
            aht_seconds,
            workload_seconds,
            asa_seconds,
            sla_target,
            service_level,
            created_date
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        );
    """


    registros = [
        (
            int(row.date_key),
            int(row.interval_key),
            int(row.skill_key),
            int(row.volume_offered),
            int(row.volume_answered),
            int(row.volume_abandoned),
            int(row.aht_seconds),
            int(row.workload_seconds),
            int(row.asa_seconds),
            float(row.sla_target),
            float(row.service_level),
            row.created_date
        )
        for row in df_demand.itertuples(
            index=False
        )
    ]


    print()
    print(
        "Inserindo registros no PostgreSQL..."
    )

    cursor.executemany(
        sql_insert,
        registros
    )

    conexao.commit()

    print()
    print("=" * 50)
    print("CARGA CONCLUÍDA COM SUCESSO")
    print("=" * 50)

    cursor.close()


except Exception as erro:

    conexao.rollback()

    print()
    print("=" * 50)
    print("ERRO DURANTE A CARGA")
    print("=" * 50)
    print(erro)

    raise


finally:

    conexao.close()

    print()
    print("Conexão encerrada.")