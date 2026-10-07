import sys
from pathlib import Path

import psycopg


# ============================================================
# CONFIGURAÇÃO DO PROJETO
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

sys.path.append(str(ROOT_DIR))


# ============================================================
# IMPORTAÇÕES DO PROJETO
# ============================================================

from conexao_db import obter_conexao
from src.generation.gerar_dim_agent import gerar_agentes


# ============================================================
# CONFIGURAÇÕES
# ============================================================

TOTAL_ESPERADO = 5000


# ============================================================
# CARGA DA DIM_AGENT
# ============================================================

def carregar_dim_agent():

    print("\n==========================================")
    print("CARGA DA DIM_AGENT")
    print("==========================================")


    # --------------------------------------------------------
    # 1. GERAÇÃO DOS AGENTES
    # --------------------------------------------------------

    df = gerar_agentes()

    print(
        f"\nAgentes gerados: {len(df)}"
    )


    # --------------------------------------------------------
    # 2. VALIDAÇÃO DA QUANTIDADE
    # --------------------------------------------------------

    if len(df) != TOTAL_ESPERADO:

        raise ValueError(
            f"Quantidade inesperada de agentes: {len(df)}"
        )


    # --------------------------------------------------------
    # 3. ABERTURA DA CONEXÃO
    # --------------------------------------------------------

    conn = obter_conexao()


    try:

        with conn.cursor() as cur:


            # ------------------------------------------------
            # 4. INSERÇÃO DOS AGENTES
            # ------------------------------------------------

            for _, row in df.iterrows():

                cur.execute(
                    """
                    INSERT INTO dim_agent (
                        agent_code,
                        agent_name,
                        agent_email,
                        team_key,
                        hire_date,
                        termination_date,
                        agent_status,
                        employment_type,
                        is_active,
                        created_date
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
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
                        row["agent_code"],
                        row["agent_name"],
                        row["agent_email"],
                        row["team_key"],
                        row["hire_date"],
                        row["termination_date"],
                        row["agent_status"],
                        row["employment_type"],
                        row["is_active"],
                        row["created_date"],
                    )
                )


        # ----------------------------------------------------
        # 5. CONFIRMAÇÃO DA TRANSAÇÃO
        # ----------------------------------------------------

        conn.commit()

        print(
            "\nCarga concluída com sucesso."
        )


    except Exception:

        # ----------------------------------------------------
        # 6. DESFAZ A TRANSAÇÃO EM CASO DE ERRO
        # ----------------------------------------------------

        conn.rollback()

        print(
            "\nErro durante a carga."
        )

        print(
            "Nenhum registro foi confirmado no banco."
        )

        raise


    finally:

        # ----------------------------------------------------
        # 7. ENCERRAMENTO DA CONEXÃO
        # ----------------------------------------------------

        conn.close()

        print(
            "Conexão encerrada."
        )


    print("\n==========================================")
    print("CARGA FINALIZADA")
    print("==========================================")


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    carregar_dim_agent()