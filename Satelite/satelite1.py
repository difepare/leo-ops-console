import csv
from datetime import datetime, timedelta
import random

start = datetime(2026, 8, 6, 12, 0, 0)
rows = []

# estado inicial
battery = 92.0
power = 35.0
temp_int = 28.0
temp_panel = 25.0
signal_db = -55.0
latency = 45.0
loss = 0.2
cpu = 25.0

for minute in range(60):
    ts = start + timedelta(minutes=minute)

    # --- escenarios por tramo ---
    if 16 <= minute <= 25:
        # carga de trabajo
        cpu = min(95, cpu + random.uniform(1.5, 3.0))
        power = min(90, power + random.uniform(1.0, 2.5))
        temp_int = min(70, temp_int + random.uniform(0.4, 1.0))
        battery -= random.uniform(0.6, 1.0)
    elif 26 <= minute <= 35:
        # degradación de enlace
        signal_db = max(-95, signal_db - random.uniform(0.8, 1.6))
        latency = min(250, latency + random.uniform(4, 10))
        loss = min(12, loss + random.uniform(0.2, 0.6))
        battery -= random.uniform(0.2, 0.4)
    elif 36 <= minute <= 45:
        # doble estrés
        cpu = min(98, cpu + random.uniform(0.5, 1.2))
        temp_int = min(75, temp_int + random.uniform(0.3, 0.8))
        signal_db = max(-98, signal_db - random.uniform(0.3, 0.8))
        latency = min(260, latency + random.uniform(2, 6))
        loss = min(15, loss + random.uniform(0.1, 0.4))
        battery -= random.uniform(0.5, 0.9)
    elif minute >= 46:
        # recuperación
        cpu = max(20, cpu - random.uniform(1.5, 3.0))
        power = max(25, power - random.uniform(1.0, 2.0))
        temp_int = max(20, temp_int - random.uniform(0.4, 0.9))
        signal_db = min(-52, signal_db + random.uniform(0.8, 1.5))
        latency = max(30, latency - random.uniform(4, 9))
        loss = max(0.0, loss - random.uniform(0.2, 0.5))
        battery -= random.uniform(0.05, 0.15)
    else:
        # normal
        cpu += random.uniform(-1.0, 1.0)
        power += random.uniform(-1.0, 1.0)
        temp_int += random.uniform(-0.3, 0.3)
        temp_panel += random.uniform(-0.5, 0.8)
        signal_db += random.uniform(-0.4, 0.4)
        latency += random.uniform(-2, 2)
        loss = max(0.0, loss + random.uniform(-0.1, 0.1))
        battery -= random.uniform(0.05, 0.12)

    # límites suaves de realismo
    cpu = min(100, max(0, cpu))
    power = min(120, max(10, power))
    temp_int = min(90, max(-10, temp_int))
    temp_panel = min(100, max(-30, temp_panel))
    signal_db = min(-40, max(-100, signal_db))
    latency = min(300, max(10, latency))
    loss = min(20, max(0, loss))
    battery = min(100, max(0, battery))

    rows.append([
        ts.isoformat(timespec="seconds"),
        round(battery, 2),
        round(power, 2),
        round(temp_int, 2),
        round(temp_panel, 2),
        round(signal_db, 2),
        round(latency, 2),
        round(loss, 2),
        round(cpu, 2),
    ])

with open("telemetry_hour.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "timestamp",
        "battery_percent",
        "power_consumption_watts",
        "internal_temp_c",
        "panel_temp_c",
        "link_signal_quality_db",
        "link_latency_ms",
        "packet_loss_percent",
        "cpu_usage_percent",
    ])
    writer.writerows(rows)

print("OK -> telemetry_hour.csv generado con", len(rows), "filas")