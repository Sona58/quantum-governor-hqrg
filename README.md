# HQRG: Hybrid Quantum Resource Governor

[![Full Lifecycle Pipeline](https://github.com/Sona58/quantum-governor-hqrg/actions/workflows/ci-cd.yaml/badge.svg)](https://github.com/your-username/hqrg/actions)
![Kubernetes](https://img.shields.io/badge/Orchestration-Kubernetes-blue)
![Terraform](https://img.shields.io/badge/IaC-Terraform-623CE4)
![Qiskit](https://img.shields.io/badge/Quantum-Qiskit-6929C4)

**HQRG** is an enterprise-grade microservices architecture designed to orchestrate and govern hybrid quantum-classical workloads. It dynamically routes financial risk analysis requests between local classical simulators and real IBM Quantum (QPU) hardware based on loan value, user tier, and cost-efficiency constraints.

## 🏗️ Architecture Overview

The system is built on a "Saga-inspired" event-driven architecture using **NATS JetStream** for reliable messaging and **Terraform** for infrastructure lifecycle management.

* **Gateway API:** FastAPI-based entry point that implements the Governance Layer.
* **Risk Engine (QML):** Quantum Neural Network (QNN) using Qiskit 2.x to perform loan risk assessments.
* **Cost Analyzer:** Observability service that tracks QPU "Credit" usage and updates a Redis audit log.
* **Infrastructure:** Automated deployment of NATS, Redis, and Python workloads via Terraform.



## 🛠️ Tech Stack

* **Quantum:** Qiskit (Aer Simulator & IBM Runtime)
* **Orchestration:** Kubernetes (Minikube/Cloud), Terraform
* **Messaging:** NATS JetStream (Event-driven)
* **Data:** Redis (Real-time Audit Logs)
* **DevOps:** GitHub Actions, Docker, PyTest (Unit, Integration, E2E)

## 🚀 Getting Started

### Prerequisites
* Docker & Kubernetes (Minikube recommended)
* Terraform 1.5+
* NATS CLI
* IBM Quantum API Token (for Enterprise tier)

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
  
---

## 🧪 Testing Strategy

The project maintains a 3-tier testing pyramid to ensure reliability across hybrid environments:

* **Unit Tests:** Logic-only testing of loan tiering and cost multipliers using Mocks.
* **Integration Tests:** Validates NATS JetStream persistence and Redis connectivity.
* **E2E Tests:** Simulates a full "Loan Request to Audit Log" lifecycle in a GitHub Actions runner using Service Containers.

Run tests locally:
```bash
pytest tests/
```

---

## 🔐 Governance & Security

* **Dynamic Secrets:** IBM API tokens are never stored in YAML. They are injected into the cluster at runtime via Terraform and Kubernetes Secrets.
* **Resource Quotas:** Hard limits are enforced at the K8s Namespace level to prevent Qiskit simulators from consuming excessive cluster resources.
* **Cost Auditing:** Every QPU execution is tracked and logged in Redis to provide real-time visibility into quantum spend.

---

## 📈 CI/CD Pipeline

The included GitHub Action automates the following on every push:

* **Lints and Unit Tests** Python code.
* **Builds Docker Images** for all microservices.
* **Spins up NATS/Redis sidecars** to run Integration and E2E tests.
* **Terraform Plan** validates infrastructure changes.