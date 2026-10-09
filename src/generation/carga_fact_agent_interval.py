import sys
from pathlib import Path

# Adiciona a raiz do projeto ao PYTHONPATH
sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

import psycopg

from conexao_db import obter_conexao

from gerar_fact_agent_interval import (
    gerar_fact_agent_interval,
    SEED,
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

CHUNK_SIZE = 5_000

# Teste inicial.
# Vamos processar apenas 100 escalas antes da carga completa.
LIMITE_SCHEDULES = None


# ============================================================
# BUSCA DAS ESCALAS
# ============================================================

def buscar_schedules(cursor, limite=None):

    sql = """
        SELECT
            fs.schedule_key,
            fs.date_key,
            fs.agent_key,
            fs.team_key,
            fs.shift_key,
            fs.skill_key,
            fs.planned_start_datetime,
            fs.planned_end_datetime,
            ds.shift_name,
            ds.duration_minutes
        FROM fact_schedule fs
        INNER JOIN dim_shift ds
            ON ds.shift_key = fs.shift_key
        ORDER BY
            fs.schedule_key
    """

    if limite is not None:
        sql += """
            LIMIT %s
        """

        cursor.execute(
            sql,
            (limite,)
        )

    else:
        cursor.execute(sql)

    return cursor.fetchall()


# ============================================================
# BUSCA DOS INTERVALOS
# ============================================================

def buscar_intervals(cursor):

    cursor.execute(
        """
        SELECT
            interval_key,
            start_time,
            end_time
        FROM dim_interval
        ORDER BY interval_key;
        """
    )

    return cursor.fetchall()


# ============================================================
# INSERÇÃO DO LOTE
# ============================================================

def inserir_lote(cursor, lote):

    sql = """
        INSERT INTO fact_agent_interval (

            date_key,
            interval_key,

            agent_key,
            team_key,
            skill_key,

            schedule_key,

            operational_status,
            activity_type,

            scheduled_flag,
            present_flag,
            available_flag,
            productive_flag,

            scheduled_minutes,

            planned_pause_minutes,
            unplanned_pause_minutes,

            training_minutes,
            meeting_minutes,
            coaching_minutes,
            administrative_minutes,
            technical_issue_minutes,

            available_minutes,
            productive_minutes,

            handling_seconds,
            contacts_handled,

            created_date

        )
        VALUES (

            %(date_key)s,
            %(interval_key)s,

            %(agent_key)s,
            %(team_key)s,
            %(skill_key)s,

            %(schedule_key)s,

            %(operational_status)s,
            %(activity_type)s,

            %(scheduled_flag)s,
            %(present_flag)s,
            %(available_flag)s,
            %(productive_flag)s,

            %(scheduled_minutes)s,

            %(planned_pause_minutes)s,
            %(unplanned_pause_minutes)s,

            %(training_minutes)s,
            %(meeting_minutes)s,
            %(coaching_minutes)s,
            %(administrative_minutes)s,
            %(technical_issue_minutes)s,

            %(available_minutes)s,
            %(productive_minutes)s,

            %(handling_seconds)s,
            %(contacts_handled)s,

            %(created_date)s

        );
    """

    cursor.executemany(
        sql,
        lote
    )


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():

    print("=" * 70)
    print("GERAÇÃO DA FACT_AGENT_INTERVAL")
    print("=" * 70)

    print(f"SEED: {SEED}")
    print(f"CHUNK SIZE: {CHUNK_SIZE}")
    print(f"LIMITE DE ESCALAS: {LIMITE_SCHEDULES}")

    connection = obter_conexao()

    try:

        cursor = connection.cursor()

        # ====================================================
        # BUSCAR ESCALAS
        # ====================================================

        print("\nBuscando escalas...")

        schedules = buscar_schedules(
            cursor,
            limite=LIMITE_SCHEDULES
        )

        print(
            f"Escalas encontradas: {len(schedules):,}"
        )

        if not schedules:

            raise RuntimeError(
                "Nenhuma escala encontrada em fact_schedule."
            )

        # ====================================================
        # BUSCAR INTERVALOS
        # ====================================================

        print("\nBuscando intervalos...")

        intervals = buscar_intervals(cursor)

        print(
            f"Intervalos encontrados: {len(intervals)}"
        )

        if not intervals:

            raise RuntimeError(
                "Nenhum intervalo encontrado em dim_interval."
            )

        # ====================================================
        # GERAR FACT_AGENT_INTERVAL
        # ====================================================

        print("\nIniciando geração dos intervalos...")

        total_registros = 0
        total_lotes = 0

        gerador = gerar_fact_agent_interval(
            schedules=schedules,
            intervals=intervals,
            chunk_size=CHUNK_SIZE,
        )

        # ====================================================
        # INSERIR LOTES
        # ====================================================

        for lote in gerador:

            inserir_lote(
                cursor,
                lote
            )

            connection.commit()

            total_registros += len(lote)
            total_lotes += 1

            print(
                f"Lote {total_lotes:>3} | "
                f"Registros inseridos: "
                f"{total_registros:,}"
            )

        # ====================================================
        # RESULTADO
        # ====================================================

        print("\n" + "=" * 70)
        print("TESTE CONCLUÍDO COM SUCESSO")
        print("=" * 70)

        print(
            f"Escalas processadas: "
            f"{len(schedules):,}"
        )

        print(
            f"Registros gerados: "
            f"{total_registros:,}"
        )

        print(
            f"Lotes processados: "
            f"{total_lotes:,}"
        )

        cursor.close()

    except Exception as erro:

        connection.rollback()

        print("\nERRO DURANTE A CARGA:")
        print(erro)

        raise

    finally:

        connection.close()

        print("\nConexão encerrada.")


# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":

    main()