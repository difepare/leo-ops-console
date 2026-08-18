import pandas as pd
from collections import Counter

df = pd.read_csv("telemetry_hour.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

alerts = []

# Umbrales (sev 1)
for _, row in df.iterrows():
    t = row["timestamp"]
    if 25 <= row["battery_percent"] < 50:
        alerts.append((t, "BATERIA_PRECAUCION", 1))
    if 60 < row["cpu_usage_percent"] <= 80:
        alerts.append((t, "CPU_PRECAUCION", 1))
    if 45 < row["internal_temp_c"] <= 55:
        alerts.append((t, "TEMP_PRECAUCION", 1))
    if 120 < row["link_latency_ms"] <= 200:
        alerts.append((t, "LATENCIA_PRECAUCION", 1))
    if 1 < row["packet_loss_percent"] <= 5:
        alerts.append((t, "LOSS_PRECAUCION", 1))
    if -85 <= row["link_signal_quality_db"] < -70:
        alerts.append((t, "SENAL_PRECAUCION", 1))

# Tendencias (sev 2)
window = 5
for i in range(window, len(df)):
    now = df.iloc[i]
    prev = df.iloc[i - window]
    t = now["timestamp"]
    if now["battery_percent"] - prev["battery_percent"] <= -3:
        alerts.append((t, "DRENAJE_BATERIA", 2))
    if now["internal_temp_c"] - prev["internal_temp_c"] >= 3:
        alerts.append((t, "CALENTAMIENTO", 2))
    if now["link_latency_ms"] - prev["link_latency_ms"] >= 30:
        alerts.append((t, "ENLACE_EMPEORANDO", 2))

# Compuestas (sev 3-5)
for _, row in df.iterrows():
    t = row["timestamp"]
    stress = (row["cpu_usage_percent"] > 60) and (row["internal_temp_c"] > 45)
    link_bad = (row["link_signal_quality_db"] < -70) and (row["link_latency_ms"] > 120) and (row["packet_loss_percent"] > 1)
    energy = (row["battery_percent"] < 50) and (row["power_consumption_watts"] > 60)

    if link_bad:
        alerts.append((t, "ENLACE_DEGRADADO", 3))
    if stress:
        alerts.append((t, "ESTRES_TERMICO", 4))
    if energy:
        alerts.append((t, "RIESGO_ENERGETICO", 4))
    if stress and link_bad:
        alerts.append((t, "DOBLE_PELIGRO", 5))

max_sev = max([a[2] for a in alerts], default=0)
types = set([a[1] for a in alerts if a[2] == max_sev])

# Recomendación por severidad máxima
if max_sev >= 5:
    action = "MODO_SEGURO"
    detail = "Reducir a funciones vitales. Estabilizar termica y enlace antes de recuperar carga."
elif max_sev == 4 and "ESTRES_TERMICO" in types:
    action = "REDUCIR_CPU_Y_ENFRIAR"
    detail = "Bajar procesos no esenciales y priorizar disipacion termica."
elif max_sev == 4 and "RIESGO_ENERGETICO" in types:
    action = "CORTAR_NO_ESENCIALES"
    detail = "Apagar sensores secundarios y preservar energia para comunicacion."
elif max_sev == 3:
    action = "BAJAR_TASA_Y_PRIORIZAR_TELEMETRIA"
    detail = "Reducir ancho de banda, reintentar enlace, enviar solo datos criticos."
elif max_sev == 2:
    action = "VIGILANCIA_ACTIVA"
    detail = "No hay critico aun, pero hay deterioro. Aumentar monitoreo y preparar mitigacion."
else:
    action = "MONITOREO_NORMAL"
    detail = "Solo precauciones. Continuar operacion estandar."

print("===== COPILOTO DE MISION =====")
print(f"Total alertas: {len(alerts)}")
print(f"Severidad maxima: {max_sev}/5")
print(f"Tipos en severidad maxima: {', '.join(sorted(types)) if types else 'N/A'}")
print()
print(f"RECOMENDACION: {action}")
print(f"Detalle: {detail}")
print()

# Top 5 de mayor severidad para contexto
top = sorted(alerts, key=lambda a: (-a[2], a[0]))[:5]
print("--- Contexto (Top 5) ---")
for a in top:
    print(f"sev={a[2]} | {a[0]} | {a[1]}")