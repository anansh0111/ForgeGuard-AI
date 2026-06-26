"""
simulator.py — ForgeGuard AI Sensor Simulator
Generates realistic sensor readings every INTERVAL_SECONDS and pushes them
through the full predict → recommend pipeline.
"""

import os
import time
import random
import logging
import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SIMULATOR] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
INTERVAL = float(os.getenv("INTERVAL_SECONDS", "5"))

# Machine IDs that the simulator will cycle through
MACHINE_IDS = [f"M-{i:03d}" for i in range(1, 6)]

# Sensor value ranges (realistic for industrial CNC machines)
RANGES = {
    "Air_temperature__K_": (298.0, 304.0),
    "Process_temperature__K_": (308.0, 314.0),
    "Rotational_speed__rpm_": (1168.0, 2860.0),
    "Torque__Nm_": (3.8, 76.6),
    "Tool_wear__min_": (0.0, 253.0),
}


def generate_reading(machine_id: str) -> dict:
    air_temp = round(random.uniform(*RANGES["Air_temperature__K_"]), 2)
    proc_temp = round(random.uniform(*RANGES["Process_temperature__K_"]), 2)
    rpm = round(random.uniform(*RANGES["Rotational_speed__rpm_"]), 1)
    torque = round(random.uniform(*RANGES["Torque__Nm_"]), 2)
    tool_wear = round(random.uniform(*RANGES["Tool_wear__min_"]), 1)
    temp_diff = round(proc_temp - air_temp, 4)

    return {
        "machine_id": machine_id,
        "Air_temperature__K_": air_temp,
        "Process_temperature__K_": proc_temp,
        "Rotational_speed__rpm_": rpm,
        "Torque__Nm_": torque,
        "Tool_wear__min_": tool_wear,
        "temp_difference": temp_diff,
    }


def wait_for_backend(client: httpx.Client, retries: int = 30, delay: float = 3.0):
    log.info("Waiting for backend to become ready...")
    for attempt in range(retries):
        try:
            r = client.get(f"{BACKEND_URL}/health", timeout=5)
            if r.status_code == 200:
                log.info("Backend is ready.")
                return
        except Exception:
            pass
        log.info(f"  Attempt {attempt + 1}/{retries} — retrying in {delay}s")
        time.sleep(delay)
    raise RuntimeError("Backend never became available. Exiting.")


def run_cycle(client: httpx.Client, machine_id: str):
    reading = generate_reading(machine_id)

    # 1. Predict
    pred_resp = client.post(f"{BACKEND_URL}/predict", json=reading, timeout=10)
    pred_resp.raise_for_status()
    pred = pred_resp.json()
    prob = pred["failure_probability"]

    log.info(
        f"[{machine_id}] prob={prob:.4f} pred={pred['failure_prediction']} "
        f"(air={reading['Air_temperature__K_']}K rpm={reading['Rotational_speed__rpm_']})"
    )

    # 2. Recommend
    rec_payload = {"machine_id": machine_id, "failure_probability": prob}
    rec_resp = client.post(f"{BACKEND_URL}/recommend", json=rec_payload, timeout=10)
    rec_resp.raise_for_status()
    rec = rec_resp.json()

    log.info(f"[{machine_id}] → severity={rec['severity']} | {rec['action']}")


def main():
    with httpx.Client() as client:
        wait_for_backend(client)

        log.info(f"Simulator running. Interval: {INTERVAL}s | Machines: {MACHINE_IDS}")
        idx = 0
        while True:
            machine_id = MACHINE_IDS[idx % len(MACHINE_IDS)]
            try:
                run_cycle(client, machine_id)
            except Exception as e:
                log.error(f"[{machine_id}] Cycle failed: {e}")

            idx += 1
            time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
