# HQRG: Hybrid Quantum Resource Governor

![Full Lifecycle Pipeline](https://github.com/Sona58/quantum-governor-hqrg/actions/workflows/ci-cd.yaml/badge.svg)](https://github.com/Sona58/hqrg/actions)
![Kubernetes](https://img.shields.io/badge/Orchestration-Kubernetes-blue)
![Terraform](https://img.shields.io/badge/IaC-Terraform-623CE4)
![Qiskit](https://img.shields.io/badge/Quantum-Qiskit-6929C4)
![Grafana](https://img.shields.io/badge/Observability-Grafana-F46800)

**HQRG** is an enterprise-grade microservices architecture designed to orchestrate and govern hybrid quantum-classical workloads. It dynamically routes financial risk analysis requests between local classical simulators, high perfromance computing (SLURM) and real IBM Quantum (QPU) hardware based on workload complexity and cost-efficiency constraints.

## 🏗️ Architecture Overview

The system utilizes and event-based "Saga" pattern managed via **NATS JetStream** and automated via **Terraform**.

* **Governance Gateway (FastAPI):** Implements an `HPC-ROUTER` logic. It automatically offloads complex quantum circuits (multi-feature payloads) to **SLURM** while keeping simpler risk assessments in the local **Risk Engine**.
* **Risk Engine (QML):** A Quantum Machine Learning service using **Qiskit Aer** and **IBM Runtime** to perform loan risk assessments via Quantum Network Networks (QNN).
* **Quantum Observability Stack:** Full-spectrum monitoring using **Prometheus** and **Grafana**, tracking QPU Latency (95th percentile), NATS message throughput, and circuit execution totals.
* **Persistence Layer:** **Redis** for real-time audit logs and **NATS Jetstream** for guaranteed message delivery of quantum jobs.

## 📊 Observability & Metrics

The system exposes a custom Grafana dashboard for real-time quantum governance:
*   **Active Risk Jobs:** Real-time counter of circuit executions.
*   **QPU Latency:** Histogram analysis of quantum inference duration.
*   **NATS Throughput:** Message velocity across the `QUANTUM` stream.
*   **Resource Health:** Memory tracking for memory-intensive Qiskit simulations.

[!Grafana-Dashboard](./images/grafana-dashboard.png)

## 🛠️ Tech Stack

*   **Quantum:** Qiskit 2.x (Aer & IBM Runtime)
*   **Orchestration:** Kubernetes (Minikube), Terraform
*   **Messaging:** NATS JetStream (Persistent Streams)
*   **Observability:** Prometheus & Grafana
*   **DevOps:** GitHub Actions (Local Minikube Runner), Docker

## 🚀 Getting Started

### Prerequisites
*   Docker & Kubernetes (Minikube)
*   Terraform 1.5+
*   NATS CLI (`nats-box`)

### Quick Start
1. **Clone the repo:**
   ```bash
   git clone [https://github.com/Sona58/quantum-governor-hqrg.git](https://github.com/Sona58/quantum-governor-hqrg.git)
   cd quantum-governor-hqrg
   ```
   
2. **Configure Environment:**
   Create a `.env` file in the root directory:
   ```bash
   IBM_QUANTUM_TOKEN=your_actual_token_here
   ```
   
3. **Initialize the Stack:**
   The master management script handles the entire lifecycle:
   ```bash
   chmod +x scripts/manage.sh
   ./scripts/manage.sh init
   ```
   
4. **Bootstrap the Quantum Stream:**
    Since NATS JetStream requires explicit stream creation, use the provided helper:
    ```bash
    kubectl run nats-bootstrap -it --rm --image=natsio/nats-box -n hqrg-core -- nats str add QUANTUM --server=nats-service:4222 --subjects "quantum.*" --defaults
    ```
    
5. 3.  **Access the Dashboard:**
    ```bash
    kubectl port-forward service/grafana-service 3000:3000 -n hqrg-core
    ```
  
---

## 🧪 Testing & CI/CD

The pipeline uses a **Local-in-Cloud** strategy to keep costs at zero while maintaining high fidelity:

*   **CI Environment:** GitHub Actions spins up a dedicated **Minikube** instance inside the runner.
*   **Artifacts:** Images are built directly into the Minikube Docker daemon (`eval $(minikube docker-env)`).
*   **Integration Tests:** Validates the full circuit from Gateway -> NATS -> Risk Engine -> Redis.

Run tests locally:
```bash
pytest tests/
```

---

## 🔐 Governance Rules

* **HPC Offloading:** Requests exceeding the feature threshold are automatically routed to SLURM to prevent local resource exhaustion.
* **Resource Quotas:** `hqrg-compute-quota` enforces strict limits on Python pods to prevent runaway Qiskit simulations.
* **Secret Management:** IBM Quantum tokens are injected as Kubernetes Secrets via Terraform and are never logged or stored in plaintext.
