import sys
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from conexao_db import obter_conexao
from src.generation.gerar_bridge_agent_skill import (
    preparar_agentes_com_operacao,
    gerar_bridge_agent_skill,
)


def carregar_bridge_agent_skill():

    print("\n==========================================")
    print("CARGA DA BRIDGE_AGENT_SKILL")
    print("==========================================")

    conn = obter_conexao()

    try:

        # ------------------------------------------
        # 1. Buscar agentes e suas equipes
        # ------------------------------------------

        df_agentes = pd.read_sql(
            """
            SELECT
                agent_key,
                team_key,
                hire_date
            FROM dim_agent
            WHERE is_active = TRUE
            ORDER BY agent_key;
            """,
            conn
        )

        print(
            f"\nAgentes ativos encontrados: "
            f"{len(df_agentes)}"
        )

        # ------------------------------------------
        # 2. Buscar operação das equipes
        # ------------------------------------------

        df_equipes = pd.read_sql(
            """
            SELECT
                team_key,
                operation_key
            FROM dim_team
            WHERE is_active = TRUE
            ORDER BY team_key;
            """,
            conn
        )

        print(
            f"Equipes encontradas: "
            f"{len(df_equipes)}"
        )

        # ------------------------------------------
        # 3. Adicionar operação aos agentes
        # ------------------------------------------

        df_agentes = preparar_agentes_com_operacao(
            df_agentes,
            df_equipes
        )

        # ------------------------------------------
        # 4. Gerar vínculos agente × skill
        # ------------------------------------------

        df_bridge = gerar_bridge_agent_skill(
            df_agentes
        )

        print(
            f"\nVínculos gerados: "
            f"{len(df_bridge)}"
        )

        # ------------------------------------------
        # 5. Inserir no PostgreSQL
        # ------------------------------------------

        with conn.cursor() as cur:

            for _, row in df_bridge.iterrows():

                cur.execute(
                    """
                    INSERT INTO bridge_agent_skill (
                        agent_key,
                        skill_key,
                        skill_level,
                        is_primary,
                        valid_from,
                        valid_to,
                        is_active
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        int(row["agent_key"]),
                        int(row["skill_key"]),
                        row["skill_level"],
                        bool(row["is_primary"]),
                        row["valid_from"],
                        row["valid_to"],
                        bool(row["is_active"]),
                    )
                )

        conn.commit()

        print("\nCarga concluída com sucesso.")

    except Exception:

        conn.rollback()

        print("\nErro durante a carga.")
        print("Nenhum registro foi confirmado no banco.")

        raise

    finally:

        conn.close()

        print("Conexão encerrada.")

    print("\n==========================================")
    print("CARGA FINALIZADA")
    print("==========================================")


if __name__ == "__main__":
    carregar_bridge_agent_skill()