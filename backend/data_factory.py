import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class industrialDataFactory:
    """
    Generates high-fidelity synthetic network telemetry.
    Uses Diurnal Cycles, Pareto Handshakes, and Multi-Metric Correlation.
    """
    def __init__(self, duration_hours=24, interval_sec=5):
        self.duration_hours = duration_hours
        self.interval_sec = interval_sec
        self.num_steps = int((duration_hours * 3600) / interval_sec)

    def generate(self, anomaly_rate=0.03, seed: int | None = None):
        if seed is not None:
            np.random.seed(seed)
        start_time = datetime.now() - timedelta(hours=self.duration_hours)
        data = []
        node_ids = [
            "Router-01", "Router-02", "Router-03", "Router-04", "Router-05",
            "Router-14", "Switch-02", "Core-DC-01", "Substation-Alpha",
            "Substation-Beta", "Regional-Hub-North", "Regional-Hub-South",
            "Node-A", "Node-B", "Node-X", "Node-Y", "Backup-Vault-01"
        ]

        latency_base = 12.0
        throughput_cap = 950.0
        
        active_anomaly = False
        anomaly_steps_remaining = 0
        pre_failure_steps = 0
        
        # Diurnal Cycle Parameters (Day/Night oscillation)
        hour_factor = 2 * np.pi / (24 * 3600 / self.interval_sec)

        for i in range(self.num_steps):
            ts = start_time + timedelta(seconds=i * self.interval_sec)
            
            # 1. DIURNAL CYCLE: Throughput oscillates based on time of day
            cycle_factor = 0.7 + 0.3 * np.sin(i * hour_factor) # Range [0.4, 1.0]
            current_throughput_base = throughput_cap * cycle_factor
            
            # 2. SENSOR DRIFT: Slow linear latency increase (simulating hardware age)
            drift_ms = (i / self.num_steps) * 4.0
            
            # Default normal values
            jitter = 1.5 + np.random.normal(0, 0.3)
            connections = int((150 + np.random.poisson(20)) * cycle_factor)
            
            if not active_anomaly and np.random.random() < anomaly_rate:
                active_anomaly = True
                pre_failure_steps = 5 
                anomaly_steps_remaining = np.random.randint(10, 20) + pre_failure_steps
                anomaly_type = np.random.choice(["ddos", "buffer_overflow", "jitter_storm", "link_degrade"])
            
            if not active_anomaly:
                latency = latency_base + drift_ms + np.random.normal(0, 0.8)
                throughput = current_throughput_base + np.random.normal(0, 15)
                pkt_loss = 0.02 + np.random.normal(0, 0.005)
                is_label = False
            else:
                if pre_failure_steps > 0:
                    # PRE-FAILURE DRIFT (The "Warning" phase)
                    factor = (6 - pre_failure_steps)
                    latency = latency_base + drift_ms + (factor * 8)
                    throughput = current_throughput_base - (factor * 30)
                    pkt_loss = 0.1 + (factor * 0.2)
                    jitter = 1.5 + (factor * 1.5)
                    pre_failure_steps -= 1
                    is_label = True
                else:
                    if anomaly_type == "ddos":
                        # DDOS SIGNATURE: Connections spike, Throughput collapses
                        connections = 2500 + np.random.poisson(500)
                        throughput = 40 + np.random.normal(0, 5)
                        latency = 450 + np.random.normal(0, 50)
                        pkt_loss = 15 + np.random.normal(0, 3)
                    elif anomaly_type == "buffer_overflow":
                        latency = 350 + np.random.normal(0, 25)
                        throughput = current_throughput_base * 0.4
                        pkt_loss = 8 + np.random.normal(0, 2)
                        jitter = 15 + np.random.normal(0, 5)
                    elif anomaly_type == "jitter_storm":
                        # Pareto-distributed jitter spikes
                        latency = latency_base + 40
                        throughput = current_throughput_base * 0.6
                        jitter = 20 + (np.random.pareto(1.1) * 80)
                        pkt_loss = 2.0
                    elif anomaly_type == "link_degrade":
                        pkt_loss = 35 + np.random.normal(0, 5)
                        throughput = current_throughput_base * 0.2
                        latency = latency_base + 100
                    
                    is_label = True

                anomaly_steps_remaining -= 1
                if anomaly_steps_remaining <= 0:
                    active_anomaly = False

            data.append({
                "timestamp": ts,
                "node_id": node_ids[i % len(node_ids)],
                "latency_ms": round(latency, 2),
                "throughput_mbps": round(max(0, throughput), 2),
                "packet_loss_pct": round(min(100, max(0, pkt_loss)), 2),
                "jitter_ms": round(min(500, max(0, jitter)), 2),
                "connections": int(max(0, connections)),
                "is_anomaly": is_label,
                "anomaly_type": anomaly_type if active_anomaly and pre_failure_steps == 0 else "none"
            })

        return pd.DataFrame(data)

if __name__ == "__main__":
    factory = industrialDataFactory()
    df = factory.generate(seed=42)
    # Save with a specific version for the "winning" demo
    df.to_csv("data/industrial_network_live.csv", index=False)
    print(f"✅ Generated High-Fidelity Industrial Telemetry.")
