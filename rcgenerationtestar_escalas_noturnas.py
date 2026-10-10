warning: in the working copy of 'src/generation/gerar_fact_agent_interval.py', LF will be replaced by CRLF the next time Git touches it
[1mdiff --git a/src/generation/gerar_fact_agent_interval.py b/src/generation/gerar_fact_agent_interval.py[m
[1mindex ac8a506..301ab10 100644[m
[1m--- a/src/generation/gerar_fact_agent_interval.py[m
[1m+++ b/src/generation/gerar_fact_agent_interval.py[m
[36m@@ -8,40 +8,14 @@[m [mfrom datetime import datetime, date, time, timedelta[m
 [m
 SEED = 42[m
 [m
[31m-random.seed(SEED)[m
[31m-[m
 [m
 # ============================================================[m
 # CONFIGURAÇÃO DAS JORNADAS[m
 # ============================================================[m
[31m-#[m
[31m-# As pausas são definidas como:[m
[31m-#[m
[31m-# percentual da jornada -> duração da pausa[m
[31m-#[m
[31m-# Exemplo:[m
[31m-#[m
[31m-# 6h:[m
[31m-# 25% -> 10 min[m
[31m-# 50% -> 20 min[m
[31m-# 75% -> 10 min[m
[31m-#[m
[31m-# 7h:[m
[31m-# 25% -> 10 min[m
[31m-# 55% -> 60 min[m
[31m-#[m
[31m-# 8h:[m
[31m-# 25% -> 10 min[m
[31m-# 50% -> 60 min[m
[31m-# 75% -> 10 min[m
[31m-#[m
[31m-# Observação:[m
[31m-# Esses valores representam uma política operacional fictícia[m
[31m-# adotada para o cenário do 3C.[m
[32m+[m[32m# Política operacional fictícia adotada para o cenário 3C.[m
 # ============================================================[m
 [m
 CONFIG_JORNADAS = {[m
[31m-[m
     "6x1_6h": {[m
         "duracao_minutos": 360,[m
         "pausas": [[m
[36m@@ -50,7 +24,6 @@[m [mCONFIG_JORNADAS = {[m
             (0.75, 10),[m
         ],[m
     },[m
[31m-[m
     "6x1_7h": {[m
         "duracao_minutos": 420,[m
         "pausas": [[m
[36m@@ -58,7 +31,6 @@[m [mCONFIG_JORNADAS = {[m
             (0.55, 60),[m
         ],[m
     },[m
[31m-[m
     "5x2_8h": {[m
         "duracao_minutos": 480,[m
         "pausas": [[m
[36m@@ -75,13 +47,11 @@[m [mCONFIG_JORNADAS = {[m
 # ============================================================[m
 [m
 CONFIG_SHRINKAGE = {[m
[31m-[m
     "Pausa Particular": {[m
         "probabilidade": 0.018,[m
         "duracao_min": 5,[m
         "duracao_max": 10,[m
     },[m
[31m-[m
     "Problema Técnico": {[m
         "probabilidade": 0.006,[m
         "duracao_min": 5,[m
[36m@@ -95,25 +65,21 @@[m [mCONFIG_SHRINKAGE = {[m
 # ============================================================[m
 [m
 CONFIG_ATIVIDADES = {[m
[31m-[m
     "Treinamento": {[m
         "probabilidade": 0.0015,[m
         "duracao_min": 30,[m
         "duracao_max": 120,[m
     },[m
[31m-[m
     "Reunião": {[m
         "probabilidade": 0.0010,[m
         "duracao_min": 30,[m
         "duracao_max": 60,[m
     },[m
[31m-[m
     "Coaching": {[m
         "probabilidade": 0.0008,[m
         "duracao_min": 30,[m
         "duracao_max": 60,[m
     },[m
[31m-[m
     "Administrativo": {[m
         "probabilidade": 0.0012,[m
         "duracao_min": 15,[m
[36m@@ -126,288 +92,145 @@[m [mCONFIG_ATIVIDADES = {[m
 # IDENTIFICAÇÃO DA JORNADA[m
 # ============================================================[m
 [m
[31m-def identificar_jornada([m
[31m-    shift_name,[m
[31m-    duration_minutes=None[m
[31m-):[m
[31m-    """[m
[31m-    Identifica a jornada operacional.[m
[31m-[m
[31m-    A identificação é feita preferencialmente pela duração[m
[31m-    da jornada, e não pelo nome do turno.[m
[31m-[m
[31m-    Isso evita dependência do padrão textual utilizado em[m
[31m-    dim_shift.shift_name.[m
[31m-[m
[31m-    Jornadas do projeto:[m
[31m-[m
[31m-        360 minutos -> 6x1_6h[m
[31m-        420 minutos -> 6x1_7h[m
[31m-        480 minutos -> 5x2_8h[m
[31m-    """[m
[31m-[m
[32m+[m[32mdef identificar_jornada(shift_name, duration_minutes=None):[m
[32m+[m[32m    """Identifica a jornada pela duração, usando o nome como fallback."""[m
     if duration_minutes is not None:[m
[31m-[m
[31m-        duration_minutes = int([m
[31m-            duration_minutes[m
[31m-        )[m
[31m-[m
[32m+[m[32m        duration_minutes = int(duration_minutes)[m
         if duration_minutes == 360:[m
             return "6x1_6h"[m
[31m-[m
         if duration_minutes == 420:[m
             return "6x1_7h"[m
[31m-[m
         if duration_minutes == 480:[m
             return "5x2_8h"[m
 [m
[31m-    # --------------------------------------------------------[m
[31m-    # Fallback pelo nome[m
[31m-    # --------------------------------------------------------[m
[31m-[m
     if shift_name:[m
[31m-[m
[31m-        shift_name = str([m
[31m-            shift_name[m
[31m-        ).lower()[m
[31m-[m
[31m-        if "6h" in shift_name:[m
[32m+[m[32m        nome = str(shift_name).lower()[m
[32m+[m[32m        if "6h" in nome:[m
             return "6x1_6h"[m
[31m-[m
[31m-        if "7h" in shift_name:[m
[32m+[m[32m        if "7h" in nome:[m
             return "6x1_7h"[m
[31m-[m
[31m-        if "8h" in shift_name:[m
[32m+[m[32m        if "8h" in nome:[m
             return "5x2_8h"[m
 [m
     raise ValueError([m
         "Não foi possível identificar a jornada. "[m
[31m-        f"shift_name={shift_name!r}, "[m
[31m-        f"duration_minutes={duration_minutes!r}"[m
[32m+[m[32m        f"shift_name={shift_name!r}, duration_minutes={duration_minutes!r}"[m
     )[m
 [m
 [m
 # ============================================================[m
[31m-# SOBREPOSIÇÃO ENTRE DOIS INTERVALOS DE DATETIME[m
[32m+[m[32m# SOBREPOSIÇÃO ENTRE INTERVALOS DE DATETIME[m
 # ============================================================[m
 [m
[31m-def calcular_sobreposicao([m
[31m-    inicio_a,[m
[31m-    fim_a,[m
[31m-    inicio_b,[m
[31m-    fim_b[m
[31m-):[m
[31m-    """[m
[31m-    Retorna a quantidade de minutos de sobreposição[m
[31m-    entre dois intervalos de datetime.[m
[31m-    """[m
[31m-[m
[31m-    inicio = max([m
[31m-        inicio_a,[m
[31m-        inicio_b[m
[31m-    )[m
[31m-[m
[31m-    fim = min([m
[31m-        fim_a,[m
[31m-        fim_b[m
[31m-    )[m
[31m-[m
[32m+[m[32mdef calcular_sobreposicao(inicio_a, fim_a, inicio_b, fim_b):[m
[32m+[m[32m    """Retorna os minutos inteiros de sobreposição entre dois intervalos."""[m
[32m+[m[32m    inicio = max(inicio_a, inicio_b)[m
[32m+[m[32m    fim = min(fim_a, fim_b)[m
     if fim <= inicio:[m
         return 0[m
[31m-[m
[31m-    segundos = ([m
[31m-        fim - inicio[m
[31m-    ).total_seconds()[m
[31m-[m
[31m-    return int([m
[31m-        round(segundos / 60)[m
[31m-    )[m
[32m+[m[32m    return int(round((fim - inicio).total_seconds() / 60))[m
 [m
 [m
 # ============================================================[m
[31m-# CRIAÇÃO DAS JANELAS DE PAUSA[m
[32m+[m[32m# CONSTRUÇÃO CORRETA DO DATETIME DE UM INTERVALO[m
 # ============================================================[m
 [m
[31m-def gerar_janelas_pausas([m
[31m-    planned_start,[m
[31m-    planned_end,[m
[31m-    jornada[m
[32m+[m[32mdef construir_intervalo_datetime([m
[32m+[m[32m    schedule_start,[m
[32m+[m[32m    schedule_end,[m
[32m+[m[32m    interval_start_time,[m
[32m+[m[32m    interval_end_time,[m
 ):[m
[31m-[m
     """[m
[31m-    Gera as janelas de pausa planejada dentro da jornada.[m
[31m-[m
[31m-    A posição da pausa é baseada em um percentual da jornada,[m
[31m-    com pequena variação aleatória para evitar que todos os[m
[31m-    agentes façam a pausa exatamente no mesmo minuto.[m
[32m+[m[32m    Constrói a ocorrência do intervalo de relógio que mais se sobrepõe[m
[32m+[m[32m    à escala. Testa a data inicial e o dia seguinte. Isso cobre jornadas[m
[32m+[m[32m    noturnas e inícios fora dos limites de 30 minutos (ex.: 18:10).[m
 [m
[31m-    As pausas são ordenadas e ajustadas para não se sobrepor.[m
[32m+[m[32m    O date_key da fact continua sendo o da escala; esta função só calcula[m
[32m+[m[32m    os datetimes usados para calcular a sobreposição.[m
     """[m
[32m+[m[32m    melhor_intervalo = None[m
[32m+[m[32m    maior_sobreposicao = -1[m
[32m+[m[32m    data_inicio = schedule_start.date()[m
 [m
[31m-    config = CONFIG_JORNADAS[jornada][m
[31m-[m
[31m-    duracao_jornada = ([m
[31m-        planned_end - planned_start[m
[31m-    ).total_seconds() / 60[m
[31m-[m
[31m-    pausas = [][m
[31m-[m
[31m-    ultima_fim = planned_start[m
[32m+[m[32m    for deslocamento_dias in (0, 1):[m
[32m+[m[32m        data_intervalo = data_inicio + timedelta(days=deslocamento_dias)[m
[32m+[m[32m        inicio = datetime.combine(data_intervalo, interval_start_time)[m
[32m+[m[32m        fim = datetime.combine(data_intervalo, interval_end_time)[m
 [m
[31m-    for percentual, duracao in config["pausas"]:[m
[32m+[m[32m        # Um intervalo como 23:30–00:00 termina no dia seguinte.[m
[32m+[m[32m        if fim <= inicio:[m
[32m+[m[32m            fim += timedelta(days=1)[m
 [m
[31m-        centro = ([m
[31m-            planned_start[m
[31m-            + timedelta([m
[31m-                minutes=duracao_jornada * percentual[m
[31m-            )[m
[32m+[m[32m        sobreposicao = calcular_sobreposicao([m
[32m+[m[32m            schedule_start, schedule_end, inicio, fim[m
         )[m
 [m
[31m-        variacao = random.randint([m
[31m-            -5,[m
[31m-            5[m
[31m-        )[m
[32m+[m[32m        if sobreposicao > maior_sobreposicao:[m
[32m+[m[32m            maior_sobreposicao = sobreposicao[m
[32m+[m[32m            melhor_intervalo = (inicio, fim)[m
 [m
[31m-        inicio = ([m
[31m-            centro[m
[31m-            + timedelta([m
[31m-                minutes=variacao[m
[31m-            )[m
[31m-            - timedelta([m
[31m-                minutes=duracao / 2[m
[31m-            )[m
[31m-        )[m
[32m+[m[32m    return melhor_intervalo[m
 [m
[31m-        fim = ([m
[31m-            inicio[m
[31m-            + timedelta([m
[31m-                minutes=duracao[m
[31m-            )[m
[31m-        )[m
 [m
[31m-        # ----------------------------------------------------[m
[31m-        # Limites da jornada[m
[31m-        # ----------------------------------------------------[m
[32m+[m[32m# ============================================================[m
[32m+[m[32m# JANELAS DE PAUSAS PLANEJADAS — UMA VEZ POR ESCALA[m
[32m+[m[32m# ============================================================[m
 [m
[31m-        limite_inicio = ([m
[31m-            planned_start[m
[31m-            + timedelta(minutes=5)[m
[31m-        )[m
[32m+[m[32mdef gerar_janelas_pausas(planned_start, planned_end, jornada, rng):[m
[32m+[m[32m    """Gera as pausas planejadas uma única vez para toda a escala."""[m
[32m+[m[32m    config = CONFIG_JORNADAS[jornada][m
[32m+[m[32m    duracao_jornada = (planned_end - planned_start).total_seconds() / 60[m
[32m+[m[32m    pausas = [][m
[32m+[m[32m    ultima_fim = planned_start[m
 [m
[31m-        limite_fim = ([m
[31m-            planned_end[m
[31m-            - timedelta(minutes=5)[m
[31m-        )[m
[32m+[m[32m    for percentual, duracao in config["pausas"]:[m
[32m+[m[32m        centro = planned_start + timedelta(minutes=duracao_jornada * percentual)[m
[32m+[m[32m        variacao = rng.randint(-5, 5)[m
[32m+[m[32m        inicio = centro + timedelta(minutes=variacao - duracao / 2)[m
[32m+[m[32m        fim = inicio + timedelta(minutes=duracao)[m
[32m+[m
[32m+[m[32m        limite_inicio = planned_start + timedelta(minutes=5)[m
[32m+[m[32m        limite_fim = planned_end - timedelta(minutes=5)[m
 [m
         if inicio < limite_inicio:[m
             inicio = limite_inicio[m
[31m-            fim = ([m
[31m-                inicio[m
[31m-                + timedelta(minutes=duracao)[m
[31m-            )[m
[32m+[m[32m            fim = inicio + timedelta(minutes=duracao)[m
 [m
         if fim > limite_fim:[m
             fim = limite_fim[m
[31m-            inicio = ([m
[31m-                fim[m
[31m-                - timedelta(minutes=duracao)[m
[31m-            )[m
[31m-[m
[31m-        # ----------------------------------------------------[m
[31m-        # Evitar sobreposição[m
[31m-        # ----------------------------------------------------[m
[32m+[m[32m            inicio = fim - timedelta(minutes=duracao)[m
 [m
         if inicio < ultima_fim:[m
[32m+[m[32m            inicio = ultima_fim + timedelta(minutes=2)[m
[32m+[m[32m            fim = inicio + timedelta(minutes=duracao)[m
 [m
[31m-            inicio = ([m
[31m-                ultima_fim[m
[31m-                + timedelta(minutes=2)[m
[31m-            )[m
[31m-[m
[31m-            fim = ([m
[31m-                inicio[m
[31m-                + timedelta(minutes=duracao)[m
[31m-            )[m
[31m-[m
[31m-        # Se não houver espaço suficiente, ignora a pausa.[m
         if fim > planned_end:[m
[31m-[m
             continue[m
 [m
[31m-        pausas.append([m
[31m-            {[m
[31m-                "inicio": inicio,[m
[31m-                "fim": fim,[m
[31m-                "duracao": duracao,[m
[31m-            }[m
[31m-        )[m
[31m-[m
[32m+[m[32m        pausas.append({"inicio": inicio, "fim": fim, "duracao": duracao})[m
         ultima_fim = fim[m
 [m
     return pausas[m
 [m
 [m
 # ============================================================[m
[31m-# ATIVIDADE PLANEJADA[m
[32m+[m[32m# ATIVIDADE PLANEJADA — UMA VEZ POR ESCALA[m
 # ============================================================[m
 [m
[31m-def atividade_planejada_aleatoria([m
[31m-    planned_start,[m
[31m-    planned_end[m
[31m-):[m
[31m-[m
[31m-    """[m
[31m-    Determina se o agente terá uma atividade planejada.[m
[31m-[m
[31m-    A atividade é criada apenas se a probabilidade aleatória[m
[31m-    for atingida.[m
[31m-    """[m
[31m-[m
[32m+[m[32mdef atividade_planejada_aleatoria(planned_start, planned_end, rng):[m
[32m+[m[32m    """Sorteia no máximo uma atividade planejada para a escala inteira."""[m
     for atividade, config in CONFIG_ATIVIDADES.items():[m
[31m-[m
[31m-        if random.random() <= config["probabilidade"]:[m
[31m-[m
[31m-            duracao = random.randint([m
[31m-                config["duracao_min"],[m
[31m-                config["duracao_max"][m
[31m-            )[m
[31m-[m
[31m-            jornada_minutos = int([m
[31m-                ([m
[31m-                    planned_end - planned_start[m
[31m-                ).total_seconds() / 60[m
[31m-            )[m
[31m-[m
[31m-            # Mantém a atividade dentro da jornada.[m
[31m-            duracao = min([m
[31m-                duracao,[m
[31m-                max(15, jornada_minutos - 30)[m
[31m-            )[m
[32m+[m[32m        if rng.random() <= config["probabilidade"]:[m
[32m+[m[32m            duracao = rng.randint(config["duracao_min"], config["duracao_max"])[m
[32m+[m[32m            jornada_minutos = int((planned_end - planned_start).total_seconds() / 60)[m
[32m+[m[32m            duracao = min(duracao, max(15, jornada_minutos - 30))[m
 [m
             inicio_min = 15[m
[31m-            inicio_max = max([m
[31m-                inicio_min,[m
[31m-                jornada_minutos - duracao - 15[m
[31m-            )[m
[31m-[m
[31m-            inicio_offset = random.randint([m
[31m-                inicio_min,[m
[31m-                inicio_max[m
[31m-            )[m
[31m-[m
[31m-            inicio = ([m
[31m-                planned_start[m
[31m-                + timedelta([m
[31m-                    minutes=inicio_offset[m
[31m-                )[m
[31m-            )[m
[31m-[m
[31m-            fim = ([m
[31m-                inicio[m
[31m-                + timedelta([m
[31m-                    minutes=duracao[m
[31m-                )[m
[31m-            )[m
[32m+[m[32m            inicio_max = max(inicio_min, jornada_minutos - duracao - 15)[m
[32m+[m[32m            inicio_offset = 