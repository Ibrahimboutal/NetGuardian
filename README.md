# 🛡️ NetGuardian — AI Resilience for Critical Infrastructure

> **"NetGuardian operates even when the network itself is failing."**
>
> **Predictive Incident Response** — A 100% offline, agentic defense system powered by local multi-agent AI (Gemma 4). Engineered to **predict and prevent** cascading failures in remote utility grids, disaster zones, and critical infrastructure.

---

## 🏗️ Judge-Winning Architecture

```mermaid
graph TD
    A[Telemetry Stream] --> B[Edge Detector]
    B --> C{Anomaly?}
    C -- Yes --> D[Event Buffer]
    
    subgraph Predictive Intelligence Layer
        D --> D1[Temporal Memory]
        D1 --> E[Gemma 4 Multi-Agent Pipeline]
        
        subgraph Reasoning & Planning
            E1[🩺 Reasoning Agent] -- Reasoning Trace --> E2[🔧 Command Agent]
            E2 -- Tool Use --> T[Tooling Layer]
            T -- Simulation --> E1
        end
        
        subgraph Grounding (RAG)
            K[Experience Base] -- Retrieve --> E1
        end
    end
    
    E2 --> F[Autonomous Mitigation]
    E2 --> G[Crisis Briefing]
    
    style B fill:#1e2d4a,stroke:#3b82f6,color:#fff
    style D fill:#1e2d4a,stroke:#f59e0b,color:#fff
    style E1 fill:#0f1629,stroke:#06b6d4,color:#fff
    style E2 fill:#0f1629,stroke:#3b82f6,color:#fff
    style K fill:#1e2d4a,stroke:#10b981,color:#fff
    style T fill:#1e2d4a,stroke:#ef4444,color:#fff
```

---

## 🚀 Key Innovations

### 1. Predictive Temporal Reasoning
Unlike reactive systems, NetGuardian analyzes **event sequences** over time. It identifies the "signature" of a cascading failure (e.g., Latency Spike → Buffer Pressure → Node Drop) and predicts the next failure point **before it happens**.

### 2. Experience-Grounded RAG (Offline)
The system uses a local **Experience Base** to ground the AI's reasoning. By retrieving similar past incident patterns, the agent avoids "hallucinations" and provides remediation plans backed by historical data—all without an internet connection.

### 3. Tool-Augmented Agents (Function Calling)
NetGuardian agents don't just "talk"; they **act**. The pipeline is equipped with a Tooling Layer that allows agents to:
- `get_node_status()`: Query live telemetry.
- `simulate_impact()`: Run graph-based failure simulations.
- `execute_mitigation()`: Apply tactical isolation or reroute traffic.

---

## 🏆 The Winning Pitch: "The Resilience Edge"

**The Problem**: Critical infrastructure (power grids, defense, disaster recovery) cannot rely on cloud-based AI. If the network is failing, the cloud is unreachable.

**The Solution**: **NetGuardian**. An offline, predictive sentinel that lives on the edge. It doesn't just tell you what's broken; it tells you what's **going to break** and intervenes to save the system.

### The Demo Flow:
1. **The Watchman**: Normal operation in a disaster recovery zone.
2. **The First Strike**: A minor egress spike detected.
3. **The Grounding**: RAG Layer retrieves a "Database Exfiltration" pattern.
4. **The Prediction**: Reasoning Agent predicts a 78% probability of a cascading firewall failure within 120s.
5. **The Intervention**: Command Agent calls `execute_mitigation` to isolate the node, successfully preventing the cascade.

---

## 🧠 Multi-Agent Logic

| Agent | Role | Output |
|-------|------|--------|
| 🩺 **Reasoning** | Predictive Forensic | Reasoning Trace, Cascade Probability, Next Failure Point |
| 🔧 **Command** | Tactical Commander | Tool Execution Plan, Mitigation Steps |
| 📢 **Communicator** | Crisis Briefing | Executive Summary, Containment Status |

---

## ⚠️ Why This Wins
- **Indispensable AI**: The system uses Gemma's reasoning to make decisions under uncertainty, not just as a chatbot.
- **Native Tool Use**: Real-time integration between LLM reasoning and system commands.
- **Zero Cloud Trace**: Full privacy and resilience for high-security environments.
