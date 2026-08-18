import pandas as pd

df = pd.read_csv("telemetry_hour.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

composite = []

for _, row in df.iterrows():
    t = row["timestamp"]

    stress_thermal = (row["cpu_usage_percent"] > 60) and (row["internal_temp_c"] > 45)
    link_bad = (
        (row["link_signal_quality_db"] < -70)
        and (row["link_latency_ms"] > 120)
        and (row["packet_loss_percent"] > 1)
    )
    energy_risk = (row["battery_percent"] < 50) and (row["power_consumption_watts"] > 60)

    if stress_thermal:
        composite.append((t, "ESTRES_TERMICO", "CPU alta + temperatura alta"))

    if link_bad:
        composite.append((t, "ENLACE_DEGRADADO", "Senal debil + latencia alta + loss"))

    if energy_risk:
        composite.append((t, "RIESGO_ENERGETICO", "Bateria media/baja + consumo alto"))

    if stress_thermal and link_bad:
        composite.append((t, "DOBLE_PELIGRO", "Termico + enlace degradado simultaneo"))

print("=== ALERTAS COMPUESTAS ===")
if not composite:
    print("Sin alertas compuestas")
else:
    for c in composite:
        print(f"{c[0]} | {c[1]} | {c[2]}")
    print(f"\nTotal: {len(composite)}")

# conteo por tipo
from collections import Counter
counts = Counter([c[1] for c in composite])
print("\n=== CONTEO POR TIPO ===")
for k, v in counts.items():
    print(f"{k}: {v}")