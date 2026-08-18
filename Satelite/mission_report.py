import pandas as pd
from collections import Counter

df = pd.read_csv("telemetry_hour.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

# --- Estado final ---
last = df.iloc[-1]
first = df.iloc[0]

# --- Tendencias (ventana 5) ---
window = 5
trend = []
for i in range(window, len(df)):
    now = df.iloc[i]
    prev = df.iloc[i - window]
    if now["battery_percent"] - prev["battery_percent"] <= -3:
        trend.append("DRENAJE_BATERIA")
    if now["internal_temp_c"] - prev["internal_temp_c"] >= 3:
        trend.append("CALENTAMIENTO")
    if now["link_latency_ms"] - prev["link_latency_ms"] >= 30:
        trend.append("ENLACE_EMPEORANDO")

# --- Compuestas ---
composite = []
for _, row in df.iterrows():
    stress = (row["cpu_usage_percent"] > 60) and (row["internal_temp_c"] > 45)
    link_bad = (row["link_signal_quality_db"] < -70) and (row["link_latency_ms"] > 120) and (row["packet_loss_percent"] > 1)
    energy = (row["battery_percent"] < 50) and (row["power_consumption_watts"] > 60)

    if stress:
        composite.append(("ESTRES_TERMICO", 4))
    if link_bad:
        composite.append(("ENLACE_DEGRADADO", 3))
    if energy:
        composite.append(("RIESGO_ENERGETICO", 4))
    if stress and link_bad:
        composite.append(("DOBLE_PELIGRO", 5))

comp_counts = Counter([c[0] for c in composite])
trend_counts = Counter(trend)
max_sev = max([c[1] for c in composite], default=0)

print("===== INFORME DE MISION (1 HORA SIMULADA) =====")
print(f"Inicio: {first['timestamp']}")
print(f"Fin:    {last['timestamp']}")
print()
print("--- ESTADO FINAL ---")
print(f"Bateria: {last['battery_percent']}%")
print(f"CPU: {last['cpu_usage_percent']}%")
print(f"Temp interna: {last['internal_temp_c']} C")
print(f"Senal: {last['link_signal_quality_db']} dB")
print(f"Latencia: {last['link_latency_ms']} ms")
print(f"Perdida: {last['packet_loss_percent']}%")
print()
print("--- TENDENCIAS DETECTADAS ---")
if trend_counts:
    for k, v in trend_counts.items():
        print(f"{k}: {v}")
else:
    print("Ninguna")
print()
print("--- ALERTAS COMPUESTAS ---")
if comp_counts:
    for k, v in comp_counts.items():
        print(f"{k}: {v}")
else:
    print("Ninguna")
print(f"Severidad maxima observada: {max_sev}/5")
print()
print("--- CONCLUSION AUTOMATICA (borrador) ---")
if max_sev >= 5:
    print("La mision atraveso un estado de doble peligro.")
elif "ENLACE_DEGRADADO" in comp_counts:
    print("El riesgo dominante fue degradacion de enlace.")
elif "ESTRES_TERMICO" in comp_counts:
    print("El riesgo dominante fue estres termico.")
elif "RIESGO_ENERGETICO" in comp_counts:
    print("El riesgo dominante fue energetico.")
else:
    print("No hubo sindromes compuestos graves; revisar tendencias tempranas.")
print("Fin del informe.")