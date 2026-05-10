import requests
import time
import random
import argparse
import sys

API_BASE = "http://127.0.0.1:8000"

NODES = [
    "Core-DC-01", "Core-DC-02",
    "Router-Edge-01", "Router-Edge-02",
    "Leaf-01", "Leaf-02", "Leaf-03"
]

METRICS = ["latency_ms", "packet_loss_pct", "jitter_ms", "throughput_mbps"]

def run_stress_test(burst_size=5, delay=2):
    print(f"🚀 Starting NetGuardian Stress Test...")
    print(f"📡 Target: {API_BASE}")
    print(f"🔥 Burst Size: {burst_size} anomalies per wave")
    print(f"⏲️ Delay: {delay}s between waves")
    print("-" * 50)

    try:
        while True:
            wave_nodes = random.sample(NODES, min(len(NODES), burst_size))
            print(f"[{time.strftime('%H:%M:%S')}] Launching wave on: {', '.join(wave_nodes)}")
            
            for node in wave_nodes:
                severity = random.choice(["high", "critical"])
                metric = random.choice(METRICS)
                
                payload = {
                    "node_id": node,
                    "severity": severity,
                    "primary_metric": metric,
                    "latency_ms": random.randint(250, 450) if metric == "latency_ms" else 80,
                    "packet_loss_pct": random.randint(10, 25) if metric == "packet_loss_pct" else 1,
                    "jitter_ms": random.randint(40, 90) if metric == "jitter_ms" else 10,
                    "throughput_mbps": random.randint(20, 100) if metric == "throughput_mbps" else 800,
                }
                
                try:
                    res = requests.post(f"{API_BASE}/api/inject-anomaly?node_id={node}", json=payload, timeout=5)
                    if res.ok:
                        print(f"  ✅ Injected {severity} {metric} anomaly -> {node}")
                    else:
                        print(f"  ❌ Failed to inject {node}: {res.status_code}")
                except Exception as e:
                    print(f"  ⚠️ Error injecting {node}: {e}")
            
            print(f"⏳ Waiting {delay}s for agent processing...")
            time.sleep(delay)
            
    except KeyboardInterrupt:
        print("\n🛑 Stress test terminated by user.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NetGuardian Stress Test Tool")
    parser.add_argument("--burst", type=int, default=3, help="Anomalies per wave")
    parser.add_argument("--delay", type=int, default=10, help="Seconds between waves")
    
    args = parser.parse_args()
    run_stress_test(burst_size=args.burst, delay=args.delay)
