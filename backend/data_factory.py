import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class industrialDataFactory:
    """
    Generates high-fidelity synthetic network telemetry.
    Uses Pareto, Poisson, and Gaussian distributions for industrial realism.
    """
    def __init__(self, duration_hours=24, interval_sec=5):
        self.duration_hours = duration_hours
        self.interval_sec = interval_sec
        self.num_steps = int((duration_hours * 3600) / interval_sec)

    def generate(self, anomaly_rate=0.05):
        start_time = datetime.now() - timedelta(hours=self.duration_hours)
        data = []

        latency_base = 15.0
        throughput_base = 900.0
        
        active_anomaly = False
        anomaly_steps_remaining = 0
        pre_failure_steps = 0
        
        for i in range(self.num_steps):
            ts = start_time + timedelta(seconds=i * self.interval_sec)
            
            # Default normal values
            jitter = 2.0 + np.random.normal(0, 0.5)
            connections = 150 + np.random.poisson(10)
            
            if not active_anomaly and np.random.random() < anomaly_rate:
                active_anomaly = True
                pre_failure_steps = 3 
                anomaly_steps_remaining = np.random.randint(5, 10) + pre_failure_steps
                anomaly_type = np.random.choice(["spike", "drop", "jitter_storm"])
            
            if not active_anomaly:
                latency = latency_base + np.random.normal(0, 1)
                throughput = throughput_base + np.random.normal(0, 20)
                pkt_loss = 0.05 + np.random.normal(0, 0.01)
                is_label = False
            else:
                if pre_failure_steps > 0:
                    drift_factor = (4 - pre_failure_steps)
                    latency = latency_base + (drift_factor * 15)
                    throughput = throughput_base - (drift_factor * 50)
                    pkt_loss = 0.5 + (drift_factor * 0.5)
                    jitter = 2.0 + (drift_factor * 2)
                    pre_failure_steps -= 1
                    is_label = True
                else:
                    if anomaly_type == "spike":
                        latency = 250 + np.random.normal(0, 20)
                        throughput = 300 + np.random.normal(0, 50)
                        pkt_loss = 10 + np.random.normal(0, 2)
                        connections = 800 + np.random.poisson(100)
                    elif anomaly_type == "drop":
                        latency = 80 + np.random.normal(0, 10)
                        throughput = 50 + np.random.normal(0, 10)
                        pkt_loss = 25 + np.random.normal(0, 5)
                    elif anomaly_type == "jitter_storm":
                        # Pareto-distributed jitter spikes
                        latency = latency_base + 30
                        throughput = throughput_base * 0.7
                        pkt_loss = 1.5
                        jitter = 10 + (np.random.pareto(1.2) * 50)
                        connections = 300 + np.random.poisson(50)
                    
                    is_label = True

                anomaly_steps_remaining -= 1
                if anomaly_steps_remaining <= 0:
                    active_anomaly = False

            data.append({
                "timestamp": ts,
                "latency_ms": round(latency, 2),
                "throughput_mbps": round(throughput, 2),
                "packet_loss_pct": round(min(100, pkt_loss), 2),
                "jitter_ms": round(min(500, jitter), 2),
                "connections": int(connections),
                "is_anomaly": is_label
            })

        return pd.DataFrame(data)

if __name__ == "__main__":
    factory = industrialDataFactory()
    df = factory.generate()
    df.to_csv("c:/Users/Ibrah/NetGuardian/data/industrial_network_v4.csv", index=False)
    print(f"Generated {len(df)} records with Industrial Pareto/Poisson logic.")
