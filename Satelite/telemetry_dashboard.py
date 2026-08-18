import pandas as pd
import matplotlib.pyplot as plt

# 1) Cargar datos
df = pd.read_csv("telemetry_hour.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# 2) Último estado
last = df.iloc[-1]

def status(value, warn, crit, reverse=False):
    """
    reverse=False: crítico cuando value > crit
    reverse=True:  crítico cuando value < crit  (ej. batería, señal)
    """
    if not reverse:
        if value > crit:
            return "CRITICO"
        if value > warn:
            return "PRECAUCION"
        return "NORMAL"
    else:
        if value < crit:
            return "CRITICO"
        if value < warn:
            return "PRECAUCION"
        return "NORMAL"

print("\n=== ESTADO ACTUAL DEL SATELITE ===")
print(f"Tiempo: {last['timestamp']}")
print(f"Bateria: {last['battery_percent']}% -> {status(last['battery_percent'], 50, 25, reverse=True)}")
print(f"CPU: {last['cpu_usage_percent']}% -> {status(last['cpu_usage_percent'], 60, 80)}")
print(f"Temp interna: {last['internal_temp_c']} C -> {status(last['internal_temp_c'], 45, 55)}")
print(f"Latencia: {last['link_latency_ms']} ms -> {status(last['link_latency_ms'], 120, 200)}")
print(f"Perdida: {last['packet_loss_percent']}% -> {status(last['packet_loss_percent'], 1, 5)}")
print(f"Senal: {last['link_signal_quality_db']} dB -> {status(last['link_signal_quality_db'], -70, -85, reverse=True)}")

# 3) Alertas en toda la hora
alerts = []
for i, row in df.iterrows():
    t = row["timestamp"]
    if row["battery_percent"] < 25:
        alerts.append((t, "CRITICO", "Bateria baja"))
    elif row["battery_percent"] < 50:
        alerts.append((t, "PRECAUCION", "Bateria en precaucion"))

    if row["cpu_usage_percent"] > 80:
        alerts.append((t, "CRITICO", "CPU alta"))
    elif row["cpu_usage_percent"] > 60:
        alerts.append((t, "PRECAUCION", "CPU elevada"))

    if row["internal_temp_c"] > 55:
        alerts.append((t, "CRITICO", "Temperatura interna alta"))
    elif row["internal_temp_c"] > 45:
        alerts.append((t, "PRECAUCION", "Temperatura interna elevada"))

    if row["link_latency_ms"] > 200:
        alerts.append((t, "CRITICO", "Latencia alta"))
    elif row["link_latency_ms"] > 120:
        alerts.append((t, "PRECAUCION", "Latencia elevada"))

    if row["packet_loss_percent"] > 5:
        alerts.append((t, "CRITICO", "Perdida de paquetes alta"))
    elif row["packet_loss_percent"] > 1:
        alerts.append((t, "PRECAUCION", "Perdida de paquetes elevada"))

    if row["link_signal_quality_db"] < -85:
        alerts.append((t, "CRITICO", "Senal muy debil"))
    elif row["link_signal_quality_db"] < -70:
        alerts.append((t, "PRECAUCION", "Senal debil"))

print("\n=== ALERTAS DETECTADAS ===")
if not alerts:
    print("Sin alertas")
else:
    # muestra máximo 20 para no saturar
    for a in alerts[:20]:
        print(f"{a[0]} | {a[1]} | {a[2]}")
    print(f"Total alertas: {len(alerts)}")

# 4) Gráficas
fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)

axes[0].plot(df["timestamp"], df["battery_percent"], label="battery_percent")
axes[0].axhline(50, linestyle="--", linewidth=1)
axes[0].axhline(25, linestyle="--", linewidth=1)
axes[0].set_ylabel("%")
axes[0].set_title("Bateria")
axes[0].legend(loc="best")

axes[1].plot(df["timestamp"], df["cpu_usage_percent"], label="cpu")
axes[1].plot(df["timestamp"], df["internal_temp_c"], label="temp_int")
axes[1].set_ylabel("cpu % / temp C")
axes[1].set_title("CPU y Temperatura interna")
axes[1].legend(loc="best")

axes[2].plot(df["timestamp"], df["link_latency_ms"], label="latency_ms")
axes[2].plot(df["timestamp"], df["packet_loss_percent"], label="loss_%")
axes[2].set_ylabel("ms / %")
axes[2].set_title("Latencia y Perdida de paquetes")
axes[2].legend(loc="best")

plt.tight_layout()
plt.savefig("telemetry_dashboard.png", dpi=140)
plt.show()

print("\nOK -> telemetry_dashboard.png generado")