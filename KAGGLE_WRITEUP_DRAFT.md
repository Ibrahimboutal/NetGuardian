# NetGuardian
## Local-First Edge AI for Infrastructure Anomaly Response

NetGuardian is a local-first incident response system for remote telecom and critical infrastructure environments. It watches live telemetry, detects abnormal behavior, simulates likely failure cascades, and generates an operator-facing briefing with mitigation guidance. The goal is not to replace operators. The goal is to help them move faster, with better evidence, when connectivity is unreliable and the system is under stress.

This project was built for the Gemma 4 Good Hackathon and focuses on the Global Resilience theme. The demo shows an end-to-end workflow: telemetry replay, anomaly scoring, graph-based impact simulation, and a Gemma-backed agent layer that produces a grounded diagnosis, recommendation, and explanation.

### Problem

Remote infrastructure is often hardest to manage when it is most fragile. In disaster-prone or low-connectivity settings, operators need a system that can still detect anomalies, interpret the likely blast radius, and recommend a response without waiting on a central cloud service. Most AI prototypes stop at classification or text generation. They do not show how a real operator moves from a telemetry spike to a safe mitigation decision.

### Solution

NetGuardian turns telemetry into an incident workflow.

1. A synthetic or loaded telemetry stream is replayed in real time.
2. An IsolationForest-based detector scores each row and extracts feature attribution.
3. When an anomaly appears, a graph simulation estimates propagation and affected nodes.
4. The agent layer produces three operator outputs:
   - Diagnosis: root-cause hypotheses and reasoning trace.
   - Recommendation: mitigation choice with trade-off analysis.
   - Explanation: a concise briefing for human operators.

The result is a UI that makes detection, reasoning, and decision-making visible instead of hiding everything behind a single model label.

### Architecture

The backend is a FastAPI service that serves telemetry history and a server-sent event stream. The detector in `backend/anomaly/detector.py` trains on network telemetry and emits a normalized incident payload with a score, severity, primary metric, and feature attribution. The event pipeline in `backend/events/trigger.py` enriches that payload with simulation results and agent outputs so the UI receives one consistent incident object.

The frontend is a React/Vite dashboard that shows:

- a live metric chart,
- an anomaly feed,
- status badges and health counters,
- and an AI panel that summarizes the grounded incident response.

The UI is intentionally built around that incident contract, so the operator sees one consistent flow from detection to explanation.

### How Gemma 4 Is Used

Gemma 4 is used as the reasoning and communication layer. The agents are organized around three tasks:

- `diagnosis_agent.py` prepares a structured prompt for root-cause reasoning and can request tool grounding through functions such as `simulate_impact`, `get_node_status`, and `analyze_topology`.
- `recommendation_agent.py` converts grounded diagnosis output into a mitigation choice while explaining the trade-off.
- `explanation_agent.py` turns the incident into an operator-friendly briefing.

The model is accessed locally through an Ollama chat endpoint in `backend/agents/gemma_client.py`. If the local model is unavailable, the system falls back to deterministic JSON so the demo still works and the interface remains responsive. That makes the submission practical on limited hardware while still showing the intended Gemma-backed agent flow.

### Why This Design

I chose a hybrid design rather than a single LLM-only response for three reasons.

First, anomaly detection should be fast and deterministic. A traditional model is a better fit than asking an LLM to parse raw telemetry from scratch.

Second, failure response needs grounding. The graph simulation provides a concrete estimate of how an incident can spread across dependent nodes, which makes the agent output easier to trust.

Third, operators need a concise explanation. The final briefing is not just text; it is a summary of what was detected, what the system believes is happening, and what mitigation was selected.

### Data and Demo Flow

For the demo, the system can load telemetry from the provided dataset or generate synthetic industrial telemetry when needed. This allows the application to start quickly and still show a realistic stream of latency, throughput, jitter, packet loss, and connection changes.

The demo flow is:

1. Open the dashboard.
2. Start the telemetry stream.
3. Watch the chart and feed update.
4. Trigger or observe an anomaly.
5. Review the diagnosis, recommendation, and explanation in the AI panel.

The live UI is designed to show the full incident path in less than a minute, which matters because the video demo is the main evaluation surface.

### Technical Challenges

The main challenge was keeping the agentic story honest. A lot of demo apps claim to use an advanced model, but the actual application path is often disconnected from the UI. I fixed that by aligning the backend incident payload with the frontend components and by making the agent outputs part of the returned event object.

Another challenge was maintaining stability when local inference is unavailable. The fallback logic ensures the UI still works, which is important for judging and for reproducibility.

Finally, I had to keep the design understandable. The interface needed to feel like an operations console, not a generic chat app. That meant emphasizing telemetry, incident state, and mitigation rather than free-form conversation.

### What Makes This a Good Gemma 4 Project

NetGuardian uses Gemma 4 where it adds the most value: reasoning over grounded evidence and generating human-readable operational guidance. The model is not replacing the detector or simulation engine; it is helping explain and coordinate the response. That is a better fit for a real resilience system and a better fit for a hackathon demo that needs both technical depth and clear storytelling.

### Impact

NetGuardian is aimed at places where connectivity is unreliable and decisions are time-sensitive: telecom sites, utility infrastructure, and disaster-response environments. In those settings, the difference between a generic alert and a grounded response can be operationally significant.

The core idea is simple but practical: detect early, simulate quickly, explain clearly, and keep the workflow local-first.

### Video Storyboard

If I were pitching this live, I would show four beats:

1. The dashboard loading with live telemetry and a stable baseline.
2. An anomaly appearing in the stream and the chart shifting visibly.
3. The AI panel filling with a grounded diagnosis, mitigation choice, and short explanation.
4. The operator view making the system feel actionable instead of abstract.

That sequence tells the whole story without needing a long explanation.

### Deliverables

- Public code repository: [add your public repo link]
- Live demo: [add your public demo link]
- Video: [add your YouTube link]
- Cover image: [add your media gallery image]

### Closing

NetGuardian demonstrates how Gemma 4 can be used as part of a real operational workflow rather than just as a text generator. It combines local inference, anomaly detection, simulation, and structured explanation into a single incident response experience.

The goal is not to make a flashy chatbot. The goal is to help operators understand what is happening, why it is happening, and what to do next when the network is under stress.