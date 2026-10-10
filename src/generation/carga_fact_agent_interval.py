import argparse
import sys
import time
from pathlib import Path

# ============================================================
# CONFIGURAÇÃO DO PROJETO
# ============================================================

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from conexao_db import obter_conexao
from gerar_fact_agent_interval import gerar_fact_agent_interval, SEED

# psycopg2 → execute_values (1 INSERT multi-linha por lote).
# psycopg3 → executemany já usa pipeline, então o fallback é eficiente.
try:
    from psycopg2.extras import execute_values
except ImportError:  # pragma: no cover
    execute_values = None

CHUNK_SIZE = 20_000          # lotes maiores = menos round-trips
MAX_MINUTOS_INTERVALO = 30   # usado na validação
LOG_A_CADA = 10              # lotes

COLUNAS = (
    "date_key",
    "interval_key",
    "agent_key",
    "team_key",
    "skill_key",
    "schedule_key",
    "operational_status",
    "activity_type",
    "scheduled_flag",
    "present_flag",
    "available_flag",
    "productive_flag",
    "scheduled_minutes",
    "planned_pause_minutes",
    "unplanned_pause_minutes",
    "training_minutes",
    "meeting_minutes",
    "coaching_minutes",
    "administrative_minutes",
    "technical_issue_minutes",
    "absence_minutes",
    "available_minutes",
    "productive_minutes",
    "available_minutes_before_absence",
    "productive_minutes_before_absence",
    "handling_seconds",
    "contacts_handled",
    "created_date",
)

_LISTA_COLUNAS = ", ".join(COLUNAS)
SQL_INSERT_MULTI = (
    f"INSERT INTO fact_agent_interval ({_LISTA_COLUNAS}) VALUES %s"
)
SQL_INSERT_MANY = (
    f"INSERT INTO fact_agent_interval ({_LISTA_COLUNAS}) "
    f"VALUES ({', '.join(['%s'] * len(COLUNAS))})"
)


# ============================================================
# ARGUMENTOS CLI
# ============================================================

def argumentos_cli():
    parser = argparse.ArgumentParser(
        description=(
            "Gera, carrega e reconcilia fact_agent_interval com "
            "fact_absence. A tabela só é limpa com --limpar."
        )
    )
    parser.add_argument(
        "--limpar",
        action="store_true",
        help=(
            "Reconstrói fact_agent_interval com TRUNCATE RESTART IDENTITY "
            "na mesma transação da carga."
        ),
    )
    parser.add_argument(
        "--limite-schedules",
        type=int,
        default=None,
        help="Limita escalas para teste; permitido apenas com --dry-run.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=CHUNK_SIZE,
        help=f"Registros por lote (padrão: {CHUNK_SIZE}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Gera os registros sem inserir ou limpar tabelas.",
    )

    args = parser.parse_args()

    # Validações feitas antes de abrir conexão.
    if args.chunk_size <= 0:
        parser.error("--chunk-size deve ser maior que zero.")
    if args.limite_schedules is not None:
        if args.limite_schedules <= 0:
            parser.error("--limite-schedules deve ser maior que zero.")
        if not args.dry_run:
            parser.error("--limite-schedules só pode ser usado com --dry-run.")
    if args.dry_run and args.limpar:
        parser.error("Não combine --dry-run com --limpar.")

    return args


# ============================================================
# CONSULTAS DE ORIGEM
# ============================================================

def buscar_schedules(cursor, limite=None):
    query = """
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
        ORDER BY fs.schedule_key
    """
    params = None
    if limite is not None:
        query += " LIMIT %s"
        params = (limite,)

    cursor.execute(query, params)
    return cursor.fetchall()


def buscar_intervals(cursor):
    cursor.execute(
        """
        SELECT interval_key, start_time, end_time
        FROM dim_interval
        ORDER BY interval_key
        """
    )
    return cursor.fetchall()


# ============================================================
# INSERÇÃO DOS LOTES
# ============================================================

def inserir_lote(cursor, lote):
    """Insere o lote em uma única instrução (muito mais rápido que
    executemany row-by-row do psycopg2)."""
    linhas = [tuple(reg[c] for c in COLUNAS) for reg in lote]

    if execute_values is not None:
        execute_values(
            cursor,
            SQL_INSERT_MULTI,
            linhas,
            page_size=len(linhas),
        )
    else:
        cursor.executemany(SQL_INSERT_MANY, linhas)


# ============================================================
# RECONCILIAÇÃO COM FACT_ABSENCE
# ============================================================

SQL_RECONCILIAR = """
WITH intervalos AS (
    SELECT
        fai.agent_interval_key,
        fai.agent_key,
        fai.schedule_key,
        fai.scheduled_minutes,
        fai.available_minutes_before_absence  AS disp_antes,
        fai.productive_minutes_before_absence AS prod_antes,
        dd.full_date + di.start_time AS inicio_intervalo,
        dd.full_date + di.end_time
            + CASE
                WHEN di.end_time <= di.start_time THEN INTERVAL '1 day'
                ELSE INTERVAL '0'
              END AS fim_intervalo
    FROM fact_agent_interval fai
    INNER JOIN dim_date dd     ON dd.date_key = fai.date_key
    INNER JOIN dim_interval di ON di.interval_key = fai.interval_key
),

sobreposicoes AS (
    SELECT
        i.agent_interval_key,
        tsrange(
            GREATEST(fa.absence_start_datetime, i.inicio_intervalo),
            LEAST(fa.absence_end_datetime, i.fim_intervalo),
            '[)'
        ) AS periodo
    FROM intervalos i
    INNER JOIN fact_absence fa
        ON fa.agent_key = i.agent_key
       AND (fa.schedule_key IS NULL OR fa.schedule_key = i.schedule_key)
       AND fa.absence_start_datetime < i.fim_intervalo
       AND fa.absence_end_datetime   > i.inicio_intervalo
    WHERE i.schedule_key IS NOT NULL
),

-- Une períodos sobrepostos (evita dupla contagem) e soma os minutos.
minutos_ausencia AS (
    SELECT
        agent_interval_key,
        ROUND(
            SUM(EXTRACT(EPOCH FROM (UPPER(faixa) - LOWER(faixa))) / 60.0)
        )::INTEGER AS minutos
    FROM (
        SELECT agent_interval_key, UNNEST(range_agg(periodo)) AS faixa
        FROM sobreposicoes
        GROUP BY agent_interval_key
    ) t
    GROUP BY agent_interval_key
),

-- Cada valor derivado é calculado uma única vez.
finais AS (
    SELECT
        i.agent_interval_key,
        i.scheduled_minutes,
        c.ausencia,
        c.disponibilidade,
        CASE
            WHEN i.disp_antes <= 0 THEN 0
            ELSE LEAST(
                c.disponibilidade,
                ROUND(
                    i.prod_antes::NUMERIC * c.disponibilidade / i.disp_antes
                )::INTEGER
            )
        END AS produtividade
    FROM intervalos i
    LEFT JOIN minutos_ausencia ma
        ON ma.agent_interval_key = i.agent_interval_key
    CROSS JOIN LATERAL (
        SELECT
            LEAST(i.scheduled_minutes, COALESCE(ma.minutos, 0)) AS ausencia,
            GREATEST(
                0,
                i.disp_antes
                - LEAST(i.scheduled_minutes, COALESCE(ma.minutos, 0))
            ) AS disponibilidade
    ) c
)

UPDATE fact_agent_interval fai
SET
    absence_minutes    = f.ausencia,
    available_minutes  = f.disponibilidade,
    productive_minutes = f.produtividade,
    present_flag       = (f.ausencia < f.scheduled_minutes),
    available_flag     = (f.disponibilidade > 0),
    productive_flag    = (f.produtividade > 0)
FROM finais f
WHERE fai.agent_interval_key = f.agent_interval_key
  -- Só grava linhas que realmente mudam: menos WAL e menos bloat.
  AND (
        fai.absence_minutes    IS DISTINCT FROM f.ausencia
     OR fai.available_minutes  IS DISTINCT FROM f.disponibilidade
     OR fai.productive_minutes IS DISTINCT FROM f.produtividade
     OR fai.present_flag       IS DISTINCT FROM (f.ausencia < f.scheduled_minutes)
     OR fai.available_flag     IS DISTINCT FROM (f.disponibilidade > 0)
     OR fai.productive_flag    IS DISTINCT FROM (f.produtividade > 0)
  )
"""


def reconciliar_ausencias(cursor):
    """
    Reconcilia ausências com os intervalos dos agentes.

    - Usa períodos reais (inclusive virada de meia-noite).
    - Associa por agente e, se informado, por escala.
    - Une ausências sobrepostas (range_agg → PostgreSQL 14+).
    - Limita a ausência ao tempo escalado.
    - Recalcula a partir dos valores "before_absence" (idempotente).
    """
    print("\nReconciliando fact_absence com fact_agent_interval...")

    # Estatísticas atualizadas para o planner escolher bons joins.
    cursor.execute("ANALYZE fact_agent_interval")

    cursor.execute(SQL_RECONCILIAR)
    print(f"Intervalos alterados: {cursor.rowcount:,}")


# ============================================================
# VALIDAÇÃO DA TABELA
# ============================================================

def validar_fact_agent_interval(cursor):
    """Interrompe a transação se as principais regras forem violadas."""

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COUNT(*) FILTER (
                WHERE scheduled_minutes < 0 OR scheduled_minutes > %s
            ),
            COUNT(*) FILTER (
                WHERE absence_minutes < 0
                   OR absence_minutes > scheduled_minutes
            ),
            COUNT(*) FILTER (
                WHERE available_minutes < 0
                   OR available_minutes > available_minutes_before_absence
            ),
            COUNT(*) FILTER (
                WHERE productive_minutes < 0
                   OR productive_minutes > available_minutes
            )
        FROM fact_agent_interval
        """,
        (MAX_MINUTOS_INTERVALO,),
    )

    total, *invalidos = cursor.fetchone()
    rotulos = (
        "Minutos escalados inválidos",
        "Ausências inválidas",
        "Disponibilidades inválidas",
        "Produtividades inválidas",
    )

    print("\nValidação de fact_agent_interval")
    print(f"Total de registros: {total:,}")
    for rotulo, qtd in zip(rotulos, invalidos):
        print(f"{rotulo}: {qtd}")

    inconsistencias = sum(invalidos)
    if inconsistencias:
        raise RuntimeError(
            f"Validação reprovada: {inconsistencias} inconsistências."
        )

    print("Validação aprovada.")


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():
    args = argumentos_cli()
    inicio = time.perf_counter()

    print("=" * 72)
    print("CARGA DA FACT_AGENT_INTERVAL")
    print("=" * 72)
    print(f"SEED: {SEED}")
    print(f"CHUNK SIZE: {args.chunk_size:,}")
    print(f"LIMITE DE ESCALAS: {args.limite_schedules}")
    print(f"LIMPAR TABELA: {args.limpar}")
    print(f"DRY RUN: {args.dry_run}")

    connection = obter_conexao()
    total_registros = 0
    total_lotes = 0
    qtd_schedules = 0

    try:
        with connection.cursor() as cursor:
            if not (args.limpar or args.dry_run):
                cursor.execute(
                    "SELECT EXISTS (SELECT 1 FROM fact_agent_interval)"
                )
                if cursor.fetchone()[0]:
                    raise RuntimeError(
                        "fact_agent_interval já contém registros. "
                        "A carga foi interrompida para evitar duplicação. "
                        "Use --limpar somente após confirmar os backups "
                        "e as dependências."
                    )

            if not args.dry_run:
                # Seguro dentro de uma carga que pode ser refeita:
                # evita esperar o flush do WAL a cada lote.
                cursor.execute("SET LOCAL synchronous_commit = off")

            if args.limpar:
                print("\nLimpando fact_agent_interval dentro da transação...")
                # Sem CASCADE: preserva proteção contra dependências.
                cursor.execute(
                    "TRUNCATE TABLE fact_agent_interval RESTART IDENTITY"
                )

            print("\nBuscando escalas...")
            schedules = buscar_schedules(cursor, args.limite_schedules)
            qtd_schedules = len(schedules)
            print(f"Escalas encontradas: {qtd_schedules:,}")
            if not schedules:
                raise RuntimeError(
                    "Nenhuma escala encontrada em fact_schedule."
                )

            print("Buscando intervalos...")
            intervals = buscar_intervals(cursor)
            print(f"Intervalos encontrados: {len(intervals):,}")
            if not intervals:
                raise RuntimeError(
                    "Nenhum intervalo encontrado em dim_interval."
                )

            print("\nGerando intervalos...")
            tipo = "validados" if args.dry_run else "inseridos"

            for lote in gerar_fact_agent_interval(
                schedules=schedules,
                intervals=intervals,
                chunk_size=args.chunk_size,
            ):
                if not args.dry_run:
                    inserir_lote(cursor, lote)

                total_registros += len(lote)
                total_lotes += 1

                if total_lotes % LOG_A_CADA == 0:
                    print(
                        f"Lote {total_lotes:,} | "
                        f"Registros {tipo}: {total_registros:,}"
                    )

            if args.dry_run:
                connection.rollback()
                print(
                    "\nDRY RUN concluído: nenhuma alteração foi gravada."
                )
            else:
                reconciliar_ausencias(cursor)
                validar_fact_agent_interval(cursor)
                connection.commit()
                print("\nTransação confirmada.")

        print("\n" + "=" * 72)
        print("PROCESSAMENTO CONCLUÍDO")
        print("=" * 72)
        print(f"Escalas processadas: {qtd_schedules:,}")
        print(f"Registros gerados: {total_registros:,}")
        print(f"Lotes processados: {total_lotes:,}")
        print(f"Tempo total: {time.perf_counter() - inicio:,.1f}s")
        if args.dry_run:
            print("Nenhuma alteração foi gravada (dry run).")
        else:
            print("Carga e reconciliação concluídas.")

    except Exception as erro:
        connection.rollback()
        print("\nERRO: transação revertida.")
        print(erro)
        raise

    finally:
        connection.close()
        print("Conexão encerrada.")


if __name__ == "__main__":
    main()