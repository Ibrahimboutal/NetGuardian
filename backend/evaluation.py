import time
import random
import numpy as np
import pandas as pd
from backend.anomaly.detector import AnomalyDetector
from backend.anomaly.preprocess import FeatureEngine
from backend.data_factory import industrialDataFactory

class NetGuardianEvaluator:
    """
    Evaluation Engine for NetGuardian AI.
    Grounds performance metrics in actual ML model scores vs Moving Average baselines.
    Measures REAL detection lead/lag based on sample indices.
    """
    def __init__(self):
        self.detector = AnomalyDetector()
        self.engine = FeatureEngine()
        self.factory = industrialDataFactory(interval_sec=5)
        self.results = {
            "adaptive_ma_baseline": {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "detection_times": []},
            "net_guardian_ai": {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "detection_times": []}
        }

    def run_benchmark(self, num_iterations=200):
        print(f"Starting Honest Benchmark ({num_iterations} iterations)...")
        
        # 1. Warm up with normal industrial data
        warmup_df = self.factory.generate(anomaly_rate=0.0)
        for _, row in warmup_df.head(20).iterrows():
            self.detector.train_step(self.engine.process(row))

        # 2. Run the actual benchmark
        test_df = self.factory.generate(anomaly_rate=0.2)
        ma_window = []
        
        # Tracking for timing
        current_anomaly_start = None
        baseline_detected_this_event = False
        ai_detected_this_event = False

        for i, row in test_df.head(num_iterations).iterrows():
            features = self.engine.process(row)
            is_real_anomaly = row["is_anomaly"] # REAL GROUND TRUTH
            
            # --- Sequence Tracking ---
            if is_real_anomaly and current_anomaly_start is None:
                current_anomaly_start = i
                baseline_detected_this_event = False
                ai_detected_this_event = False
            elif not is_real_anomaly:
                current_anomaly_start = None

            # --- Baseline: Adaptive Moving Average ---
            ma_window.append(row["latency_ms"])
            if len(ma_window) > 10: ma_window.pop(0)
            ma_thresh = np.mean(ma_window) * 2.0 
            baseline_detected = row["latency_ms"] > ma_thresh or row["packet_loss_pct"] > 5.0
            
            if is_real_anomaly:
                if baseline_detected:
                    self.results["adaptive_ma_baseline"]["tp"] += 1
                    if not baseline_detected_this_event:
                        # Real lag: seconds from start of ground truth
                        lag = (i - current_anomaly_start) * self.factory.interval_sec
                        self.results["adaptive_ma_baseline"]["detection_times"].append(lag)
                        baseline_detected_this_event = True
                else:
                    self.results["adaptive_ma_baseline"]["fn"] += 1
            else:
                if baseline_detected:
                    self.results["adaptive_ma_baseline"]["fp"] += 1
                else:
                    self.results["adaptive_ma_baseline"]["tn"] += 1

            # --- NetGuardian AI: Temporal Isolation Forest ---
            is_ai_anomaly, score, severity, attribution = self.detector.predict(features, train=False)
            
            if is_real_anomaly:
                if is_ai_anomaly:
                    self.results["net_guardian_ai"]["tp"] += 1
                    if not ai_detected_this_event:
                        # Real lag/lead: seconds from start of ground truth
                        lag = (i - current_anomaly_start) * self.factory.interval_sec
                        self.results["net_guardian_ai"]["detection_times"].append(lag)
                        ai_detected_this_event = True
                else:
                    self.results["net_guardian_ai"]["fn"] += 1
            else:
                if is_ai_anomaly:
                    self.results["net_guardian_ai"]["fp"] += 1
                else:
                    self.results["net_guardian_ai"]["tn"] += 1

        return self.compute_metrics()

    def compute_metrics(self):
        metrics = {}
        for method, counts in self.results.items():
            tp, fp, fn, tn = counts["tp"], counts["fp"], counts["fn"], counts["tn"]
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            avg_lag = np.mean(counts["detection_times"]) if counts["detection_times"] else 0
            
            metrics[method] = {
                "precision": round(precision, 2),
                "recall": round(recall, 2),
                "avg_lag_sec": round(avg_lag, 1)
            }
        return metrics

if __name__ == "__main__":
    evaluator = NetGuardianEvaluator()
    results = evaluator.run_benchmark()
    print("\nHonest Evaluation Results (No Hardcoded Timings):")
    for method, m in results.items():
        print(f"--- {method.upper()} ---")
        print(f"Precision: {m['precision']}")
        print(f"Recall:    {m['recall']}")
        print(f"Avg Lag:   {m['avg_lag_sec']}s (From Anomaly Start)")
    
    # Calculate relative lead
    ai_lag = results["net_guardian_ai"]["avg_lag_sec"]
    base_lag = results["adaptive_ma_baseline"]["avg_lag_sec"]
    print(f"\nNetGuardian Lead vs Baseline: {round(base_lag - ai_lag, 1)}s faster")
