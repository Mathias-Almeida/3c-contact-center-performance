import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src" / "generation"))
sys.path.insert(0, str(ROOT))

from conexao_db import obter_conexao
from gerar_fact_agent_interval import gerar_fact_agent_interval

SCHEDULE_KEYS = (49300, 934606)


def main():
    connection = obter_conexao()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
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
                JOIN dim_shift ds ON ds.shift_key = fs.shift_key
                WHERE fs.schedule_key = ANY(%s)
                ORDER BY fs.schedule_key
                """,
                (list(SCHEDULE_KEYS),),
            )
            schedules = cursor.fetchall()
            found = {row[0] for row in schedules}
            missing = set(SCHEDULE_KEYS) - found
            if missing:
                raise RuntimeError(f"Escalas não encontradas: {sorted(missing)}")

            cursor.execute(
                """
                SELECT interval_key, start_time, end_time
                FROM dim_interval
                ORDER BY interval_key
                """
            )
            intervals = cursor.fetchall()

            cursor.execute(
                "SELECT full_date FROM dim_date WHERE full_date = ANY(%s)",
                (["2026-01-03", "2026-08-22"],),
            )
            dates_present = {str(row[0]) for row in cursor.fetchall()}

        generated = []
        for batch in gerar_fact_agent_interval(schedules, intervals, chunk_size=5000):
            generated.extend(batch)

        by_schedule = defaultdict(list)
        for row in generated:
            by_schedule[row["schedule_key"]].append(row)

        print("=" * 72)
        print("VALIDAÇÃO DIRECIONADA DE ESCALAS NOTURNAS")
        print("Nenhum dado será inserido ou alterado.")
        print("=" * 72)

        all_ok = True
        for schedule in schedules:
            key = schedule[0]
            start = schedule[6]
            end = schedule[7]
            expected = int(schedule[9])
            rows = by_schedule[key]
            total = sum(row["scheduled_minutes"] for row in rows)
            dates = sorted({str(row["date_key"]) for row in rows})
            day_groups = defaultdict(int)
            for row in rows:
                day_groups[row["date_key"]] += row["scheduled_minutes"]

            ok = total == expected
            all_ok = all_ok and ok
            print(f"\nEscala {key} | {schedule[8]}")
            print(f"Jornada: {start} até {end}")
            print(f"Minutos esperados: {expected} | gerados: {total}")
            print(f"Linhas geradas: {len(rows)}")
            print("Minutos por date_key: " + ", ".join(f"{k}: {v}" for k, v in sorted(day_groups.items())))
            print("Resultado duração: " + ("OK" if ok else "FALHOU"))

        print("\nDatas seguintes presentes em dim_date:")
        for expected_date in ("2026-01-03", "2026-08-22"):
            exists = expected_date in dates_present
            print(f"{expected_date}: {'OK' if exists else 'AUSENTE'}")
            if not exists:
                all_ok = False

        if all_ok:
            print("\nTESTE DIRECIONADO CONCLUÍDO: duração das escalas validada.")
            print("A tabela fact_agent_interval não foi modificada.")
        else:
            print("\nTESTE COM FALHAS: não execute a reconstrução ainda.")
            raise SystemExit(1)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
