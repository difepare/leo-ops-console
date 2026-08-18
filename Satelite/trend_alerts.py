import pandas as pd

df = pd.read_csv("telemetry_hour.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

window = 5  # minutos
trend_alerts = []

for i in range(window, len(df)):
    now = df.iloc[i]
    prev = df.iloc[i - window]
    t = now["timestamp"]

    d_batt = now["battery_percent"] - prev["battery_percent"]
    d_temp = now["internal_temp_c"] - prev["internal_temp_c"]
    d_lat = now["link_latency_ms"] - prev["link_latency_ms"]

    if d_batt <= -3:
        trend_alerts.append((t, "TENDENCIA", f"Drenaje de bateria: {d_batt:.2f} puntos en {window} min"))

    if d_temp >= 3:
        trend_alerts.append((t, "TENDENCIA", f"Calentamiento: +{d_temp:.2f} C en {window} min"))

    if d_lat >= 30:
        trend_alerts.append((t, "TENDENCIA", f"Enlace empeorando: +{d_lat:.2f} ms en {window} min"))

print("=== ALERTAS POR TENDENCIA ===")
if not trend_alerts:
    print("Sin alertas de tendencia")
else:
    for a in trend_alerts:
        print(f"{a[0]} | {a[1]} | {a[2]}")
    print(f"\nTotal: {len(trend_alerts)}")

# Comparar con estado puntual de la última fila
last = df.iloc[-1]
print("\n=== ESTADO FINAL ===")
print(f"Bateria: {last['battery_percent']}%")
print(f"Temp interna: {last['internal_temp_c']} C")
print(f"Latencia: {last['link_latency_ms']} ms")