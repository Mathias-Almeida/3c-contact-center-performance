
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from conexao_db import obter_conexao
from gerar_fact_absence import gerar_fact_absence, SEED

CHUNK_SIZE = 5000


def buscar_schedules(cursor):
    cursor.execute("""
        SELECT
            fs.schedule_key,
            fs.date_key,
            fs.agent_key,
            fs.planned_start_datetime,
            fs.planned_end_datetime,
            fs.planned_minutes
        FROM fact_schedule fs
        JOIN dim_agent da
            ON da.agent_key = fs.agent_key
        WHERE da.hire_date <= fs.planned_start_datetime::date
          AND (
              da.termination_date IS NULL
              OR da.termination_date >= fs.planned_start_datetime::date
          )
        ORDER BY fs.schedule_key;
    """)
    return cursor.fetchall()


def buscar_tipos(cursor):
    cursor.execute("""
        SELECT
            absence_type_code,
            absence_type_key
        FROM dim_absence_type
        WHERE is_active = TRUE
          AND impacts_absenteeism = TRUE;
    """)
    return {
        codigo: chave
        for codigo, chave in cursor.fetchall()
    }


def inserir_lote(cursor, lote):
    cursor.executemany("""
        INSERT INTO fact_absence (
            date_key,
            agent_key,
            absence_type_key,
            schedule_key,
            absence_start_datetime,
            absence_end_datetime,
            absence_minutes,
            created_date
        )
        VALUES (
            %(date_key)s,
            %(agent_key)s,
            %(absence_type_key)s,
            %(schedule_key)s,
            %(absence_start_datetime)s,
            %(absence_end_datetime)s,
            %(absence_minutes)s,
            %(created_date)s
        );
    """, lote)


def main():
    print("=" * 65)
    print("CARGA DA FACT_ABSENCE")
    print("=" * 65)
    print(f"SEED: {SEED}")
    print(f"CHUNK SIZE: {CHUNK_SIZE}")

    connection = obter_conexao()

    try:
        with connection.cursor() as cursor:
            print("\nBuscando escalas...")
            schedules = buscar_schedules(cursor)
            print(f"Escalas encontradas: {len(schedules):,}")

            print("\nBuscando tipos de ausência...")
            absence_types = buscar_tipos(cursor)
            print(f"Tipos disponíveis: {len(absence_types)}")

            tipos_necessarios = set(
                ["ABS001", "ABS002", "ABS004", "ABS008", "ABS010"]
            )
            faltantes = tipos_necessarios - set(absence_types)

            if faltantes:
                raise RuntimeError(
                    "Tipos ausentes ou inativos em dim_absence_type: "
                    + ", ".join(sorted(faltantes))
                )

            print("\nGerando e inserindo ocorrências...")
            total = 0

            for lote in gerar_fact_absence(
                schedules=schedules,
                absence_types=absence_types,
                chunk_size=CHUNK_SIZE,
            ):
                inserir_lote(cursor, lote)
                connection.commit()
                total += len(lote)
                print(f"Registros inseridos: {total:,}")

            print("\n" + "=" * 65)
            print("CARGA CONCLUÍDA")
            print("=" * 65)
            print(f"Ocorrências inseridas: {total:,}")

    except Exception as erro:
        connection.rollback()
        print(f"\nERRO: {erro}")
        raise
    finally:
        connection.close()
        print("Conexão encerrada.")


if __name__ == "__main__":
    main()
