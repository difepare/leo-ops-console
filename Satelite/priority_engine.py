import pandas as pd
from collections import Counter

df = pd.read_csv("telemetry_hour.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

alerts = []

# --- Umbrales simples (severidad 1) ---
for _, row in df.iterrows():
    t = row["timestamp"]

    if 25 <= row["battery_percent"] < 50:
        alerts.append((t, "BATERIA_PRECAUCION", 1, "Bateria en precaucion", "umbral"))
    if 60 < row["cpu_usage_percent"] <= 80:
        alerts.append((t, "CPU_PRECAUCION", 1, "CPU elevada", "umbral"))
    if 45 < row["internal_temp_c"] <= 55:
        alerts.append((t, "TEMP_PRECAUCION", 1, "Temp interna elevada", "umbral"))
    if 120 < row["link_latency_ms"] <= 200:
        alerts.append((t, "LATENCIA_PRECAUCION", 1, "Latencia elevada", "umbral"))
    if 1 < row["packet_loss_percent"] <= 5:
        alerts.append((t, "LOSS_PRECAUCION", 1, "Perdida elevada", "umbral"))
    if -85 <= row["link_signal_quality_db"] < -70:
        alerts.append((t, "SENAL_PRECAUCION", 1, "Senal debil", "umbral"))

# --- Tendencias (severidad 2) ---
window = 5
for i in range(window, len(df)):
    now = df.iloc[i]
    prev = df.iloc[i - window]
    t = now["timestamp"]

    d_batt = now["battery_percent"] - prev["battery_percent"]
    d_temp = now["internal_temp_c"] - prev["internal_temp_c"]
    d_lat = now["link_latency_ms"] - prev["link_latency_ms"]

    if d_batt <= -3:
        alerts.append((t, "DRENAJE_BATERIA", 2, f"Bateria {d_batt:.2f} pts en {window} min", "tendencia"))
    if d_temp >= 3:
        alerts.append((t, "CALENTAMIENTO", 2, f"Temp +{d_temp:.2f} C en {window} min", "tendencia"))
    if d_lat >= 30:
        alerts.append((t, "ENLACE_EMPEORANDO", 2, f"Latencia +{d_lat:.2f} ms en {window} min", "tendencia"))

# --- Compuestas (severidad 3-5) ---
for _, row in df.iterrows():
    t = row["timestamp"]

    stress = (row["cpu_usage_percent"] > 60) and (row["internal_temp_c"] > 45)
    link_bad = (
        (row["link_signal_quality_db"] < -70)
        and (row["link_latency_ms"] > 120)
        and (row["packet_loss_percent"] > 1)
    )
    energy = (row["battery_percent"] < 50) and (row["power_consumption_watts"] > 60)

    if link_bad:
        alerts.append((t, "ENLACE_DEGRADADO", 3, "Senal + latencia + loss", "compuesta"))
    if stress:
        alerts.append((t, "ESTRES_TERMICO", 4, "CPU alta + temp alta", "compuesta"))
    if energy:
        alerts.append((t, "RIESGO_ENERGETICO", 4, "Bateria baja/media + consumo alto", "compuesta"))
    if stress and link_bad:
        alerts.append((t, "DOBLE_PELIGRO", 5, "Termico + enlace simultaneo", "compuesta"))

# Orden: severidad desc, luego tiempo
alerts_sorted = sorted(alerts, key=lambda a: (-a[2], a[0]))

print("===== MOTOR DE PRIORIDAD =====")
print(f"Total alertas: {len(alerts_sorted)}\n")

print("--- TOP 15 (mayor prioridad primero) ---")
for a in alerts_sorted[:15]:
    print(f"sev={a[2]} | {a[0]} | {a[1]} | {a[4]} | {a[3]}")

sev_counts = Counter([a[2] for a in alerts_sorted])
print("\n--- CONTEO POR SEVERIDAD ---")
for s in sorted(sev_counts.keys(), reverse=True):
    print(f"Severidad {s}: {sev_counts[s]}")

type_counts = Counter([a[1] for a in alerts_sorted])
print("\n--- TIPO MAS FRECUENTE ---")
for k, v in type_counts.most_common(5):
    print(f"{k}: {v}")

max_sev = max([a[2] for a in alerts_sorted], default=0)
print(f"\nSeveridad maxima observada: {max_sev}/5")

if max_sev >= 5:
    dominant = "DOBLE_PELIGRO"
elif max_sev == 4:
    dominant = "RIESGO SERIO (termico/energetico)"
elif max_sev == 3:
    dominant = "ENLACE_DEGRADADO"
elif max_sev == 2:
    dominant = "TENDENCIAS TEMPRANAS"
else:
    dominant = "SOLO PRECAUCIONES"
print(f"Prioridad dominante de la mision: {dominant}")