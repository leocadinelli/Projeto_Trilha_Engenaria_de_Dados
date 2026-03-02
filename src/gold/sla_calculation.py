import pandas as pd
import numpy as np
from datetime import datetime

# ----------------------------
# SLA esperado por prioridade
# ----------------------------
def sla_por_prioridade(priority):

    tabela_sla = {
        'Low': 72,
        'Medium': 48,
        'High': 24
    }

    return tabela_sla.get(priority, 48)


# ----------------------------
# Cálculo do tempo real
# ----------------------------
def calcular_tempo_real(created_at, resolved_at, feriado):

    if pd.isna(resolved_at):
        return np.nan

    created_at = pd.to_datetime(created_at)
    resolved_at = pd.to_datetime(resolved_at)

    tempo = (resolved_at - created_at).total_seconds() / 3600

    # 🔴 Regra: se houve feriado no período
    # acrescenta 24h ao SLA real
    if feriado == 1:
        tempo = tempo - 24

    return tempo


# ----------------------------
# Métricas de SLA
# ----------------------------
def calcular_metricas_sla(created_at, resolved_at, priority, feriado):

    tempo_real = calcular_tempo_real(
        created_at,
        resolved_at,
        feriado
    )

    sla_esperado = sla_por_prioridade(priority)

    if pd.isna(tempo_real):
        status = 'Em aberto'
    else:
        status = 'Atendido' if tempo_real <= sla_esperado else 'Não Atendido'

    return tempo_real, sla_esperado, status