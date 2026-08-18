import csv
from datetime import datetime, timedelta
import random

start = datetime(2026, 8, 6, 12, 0, 0)
rows = []

battery = 90
power = 40
temp_int = 25
temp_panel = 20
signal_db = -55
latency = 50
loss = 0.5
cpu = 30

for minute in range(60):
    ts = start + timedelta(minutes=minute)

    # Normal (0–15)
    if minute < 16:
        cpu += random.uniform(-1, 1)
        temp_int += random.uniform(-0.3, 0.3)
        battery -= random.uniform(0.05, 0.1)

    # Carga de trabajo (16–25)
    elif minute < 26:
        cpu += random.uniform(2, 4)
        temp_int += random.uniform(0.5, 1.0)
        power += random.uniform(1, 2)
        battery -= random.uniform(0.5, 1.0)

    # Enlace degradado (26–35)
    elif minute < 36:
        signal_db -= random.uniform(1, 2)
        latency += random.uniform(5, 10)
        loss += random.uniform(0.2, 0.5)
        battery -= random.uniform(0.2, 0.4)

    # Doble estrés (36–45)
    elif minute < 46:
        cpu += random.uniform(1, 2)
        temp_int += random.uniform(0.5, 1.0)
        signal_db -= random.uniform(0.5, 1.0)
        latency += random.uniform(3, 6)
        loss += random.uniform(0.2, 0.4)
        battery -= random.uniform(0.5, 0.8)

    # Recuperación (46–60)
    else:
        cpu -= random.uniform(2, 4)
        temp_int -= random.uniform(0.5, 1.0)
        signal_db += random.uniform(1, 2)
        latency -= random.uniform(5, 10)
        loss -= random.uniform(0.2, 0.5)
        battery -= random.uniform(0.05, 0.1)

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

print("OK -> telemetry_hour.csv generado")
