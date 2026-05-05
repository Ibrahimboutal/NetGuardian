"""
NetGuardian Demo — Simulate Stream
Injects scripted anomalies into the running API for a controlled demo.

Usage:
    python demo/simulate_stream.py

Requirements:
    pip install requests
    uvicorn backend.main:app --reload   (must be running)
"""
import time
import requests
import json

API_BASE = "http://localhost:8000"


def print_banner():
    print("\n" + "=" * 60)
    print("  🛡️  NetGuardian — Demo Simulation")
    print("=" * 60)


def check_api():
    try:
        r = requests.get(f"{API_BASE}/api/health", timeout=3)
        print(f"✅ API Online: {r.json()}")
        return True
    except Exception:
        print("❌ API not reachable. Start: uvicorn backend.main:app --reload")
        return False


def show_normal_phase():
    print("\n📊 Phase 1: Normal Traffic")
    print("   All systems nominal. Latency ~13ms, packet loss ~0.1%")
    print("   ✅ No anomalies detected.")
    for i in range(3):
        print(f"   [{i+1}/3] Monitoring... latency=13ms | loss=0.1% | throughput=950Mbps")
        time.sleep(1)


def inject_anomaly():
    print("\n🔴 Phase 2: ANOMALY INJECTION")
    print("   Injecting: latency spike + packet loss surge...")
    time.sleep(1)

    r = requests.post(f"{API_BASE}/api/inject-anomaly", timeout=90)
    if r.status_code != 200:
        print(f"❌ Injection failed: {r.status_code}")
        return

    data = r.json()

    print("\n" + "─" * 60)
    print(f"  ⚠️  ANOMALY DETECTED  |  Severity: {data['severity'].upper()}")
    print(f"  Primary Metric : {data['primary_metric']}")
    print(f"  Latency        : {data['latency_ms']}ms")
    print(f"  Packet Loss    : {data['packet_loss_pct']}%")
    print(f"  Throughput     : {data['throughput_mbps']} Mbps")
    print(f"  Anomaly Score  : {data['anomaly_score']}")
    print("─" * 60)

    if data.get("agents"):
        agents = data["agents"]
        print("\n🩺 DIAGNOSIS:")
        print(f"   {agents['diagnosis']}")
        print("\n🔧 RECOMMENDATIONS:")
        for line in agents["recommendation"].strip().split("\n"):
            print(f"   {line}")
        print("\n📢 INCIDENT SUMMARY:")
        print(f"   {agents['explanation']}")

    print("\n" + "─" * 60)


def show_recovery_phase():
    print("\n✅ Phase 3: Recovery")
    print("   Traffic normalizing... latency returning to baseline.")
    for i in range(3):
        latency = 320 - (i * 100)
        print(f"   [{i+1}/3] Latency: {latency}ms — recovering...")
        time.sleep(1)
    print("   ✅ All systems stable.")


def main():
    print_banner()
    if not check_api():
        return

    show_normal_phase()
    inject_anomaly()
    show_recovery_phase()

    print("\n🎯 Demo complete. Open http://localhost:5173 for the dashboard.\n")


if __name__ == "__main__":
    main()
