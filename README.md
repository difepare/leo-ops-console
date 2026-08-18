# leo-ops-console
Mini mission operations lab for simulated LEO satellite telemetry
# LEO Ops Console

A small mission-operations lab that turns simulated satellite telemetry into alerts, priorities, and an actionable recommendation.

This project simulates one hour of a LEO satellite mission and walks through a full operations pipeline:

**telemetry → thresholds → trends → composite alerts → severity → recommendation → ops console**

## What it does

- Generates realistic telemetry for 8 signals (power, thermal, link, CPU)
- Visualizes the mission in a dashboard
- Detects early degradation with trend windows
- Diagnoses multi-signal risk patterns
- Ranks alerts by severity
- Outputs one current operational recommendation

## Why it exists

Remote systems fail in motion, not only at a red threshold.
This lab trains the idea of operating a system you cannot touch: watch signals, detect syndromes, and decide what to do first.

Sample mission result
In the current 60-minute simulation:

Dominant risk: link degradation
Max severity: 3/5
Active recommendation: reduce data rate and prioritize essential telemetry

Pipeline

Generate time-series telemetry
Flag simple threshold alerts
Detect 5-minute trends
Build composite syndromes
Rank by severity
Issue one current action

What this demonstrates

Systems thinking
Time-series monitoring
Operational decision-making
Clean problem-to-action design

Status
Educational lab / portfolio project.
Next step: root-cause hints and a lightweight web console.
Author
Diego F. Palomino

## How to run

```bash
pip install -r requirements.txt
python src/generate_telemetry.py
python src/telemetry_dashboard.py
python src/ops_console.py
