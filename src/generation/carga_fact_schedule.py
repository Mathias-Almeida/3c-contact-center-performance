import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

import pandas as pd

from conexao_db import obter_conexao
from gerar_fact_schedule import gerar_fact_schedule


def main():

    print("=" * 50)
    print("CARGA DA FACT_SCHEDULE")
    print("=" * 50)

    connection = obter_conexao()

    try:

        # ====================================================
        # DIM_AGENT
        # ====================================================

        df_agentes = pd.read_sql(
            """
            SELECT
                agent_key,
                team_key,
                hire_date,
                termination_date,
                agent_status
            FROM dim_agent
            WHERE is_active = TRUE;
            """,
            connection
        )

        print(
            f"Agentes ativos encontrados: "
            f"{len(df_agentes)}"
        )

        # ====================================================
        # DIM_TEAM
        # ====================================================

        df_equipes = pd.read_sql(
            """
            SELECT
                team_key,
                operation_key
            FROM dim_team
            WHERE is_active = TRUE;
            """,
            connection
        )

        print(
            f"Equipes encontradas: "
            f"{len(df_equipes)}"
        )

        # ====================================================
        # DIM_SHIFT
        # ====================================================

        df_shifts = pd.read_sql(
            """
            SELECT
                shift_key,
                start_time,
                end_time,
                shift_hours,
                is_overnight
            FROM dim_shift
            WHERE is_active = TRUE;
            """,
            connection
        )

        print(
            f"Shifts encontrados: "
            f"{len(df_shifts)}"
        )

        # ====================================================
        # DIM_SKILL
        # ====================================================

        df_skills = pd.read_sql(
            """
            SELECT
                skill_key,
                skill_code,
                skill_name
            FROM dim_skill
            WHERE is_active = TRUE;
            """,
            connection
        )

        print(
            f"Skills encontradas: "
            f"{len(df_skills)}"
        )

        # ====================================================
        # BRIDGE_AGENT_SKILL
        # ====================================================

        df_bridge = pd.read_sql(
            """
            SELECT
                agent_key,
                skill_key,
                is_primary
            FROM bridge_agent_skill
            WHERE is_active = TRUE;
            """,
            connection
        )

        print(
            f"Vínculos de skill encontrados: "
            f"{len(df_bridge)}"
        )

        # ====================================================
        # DIM_DATE
        # ====================================================

        df_datas = pd.read_sql(
            """
            SELECT
                date_key,
                full_date,
                is_holiday
            FROM dim_date
            ORDER BY full_date;
            """,
            connection
        )

        print(
            f"Datas encontradas: "
            f"{len(df_datas)}"
        )

        # ====================================================
        # GERAÇÃO
        # ====================================================

        df_schedule = gerar_fact_schedule(
            df_agentes=df_agentes,
            df_equipes=df_equipes,
            df_shifts=df_shifts,
            df_skills=df_skills,
            df_bridge=df_bridge,
            df_datas=df_datas
        )

        print()
        print(
            f"Escalas geradas: "
            f"{len(df_schedule)}"
        )

        # ====================================================
        # CARGA
        # ====================================================

        registros = list(
            df_schedule[
                [
                    "date_key",
                    "agent_key",
                    "team_key",
                    "shift_key",
                    "skill_key",
                    "schedule_status",
                    "planned_start_datetime",
                    "planned_end_datetime",
                    "planned_minutes",
                    "scheduled_hours",
                    "created_date"
                ]
            ].itertuples(
                index=False,
                name=None
            )
        )

        with connection.cursor() as cursor:

            cursor.executemany(
                """
                INSERT INTO fact_schedule (
                    date_key,
                    agent_key,
                    team_key,
                    shift_key,
                    skill_key,
                    schedule_status,
                    planned_start_datetime,
                    planned_end_datetime,
                    planned_minutes,
                    scheduled_hours,
                    created_date
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                );
                """,
                registros
            )

        connection.commit()

        print()
        print("=" * 50)
        print("CARGA CONCLUÍDA COM SUCESSO")
        print("=" * 50)

    except Exception as erro:

        connection.rollback()

        print()
        print("ERRO DURANTE A CARGA:")
        print(erro)

        raise

    finally:

        connection.close()

        print(
            "Conexão encerrada."
        )


if __name__ == "__main__":
    main()