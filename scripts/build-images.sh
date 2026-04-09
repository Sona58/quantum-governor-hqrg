#!/bin/bash
set -e

# If using minikube, point the docker-cli to minikube's registry
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    echo "🐳 [BUILD] Pointing Docker to Minikube registry..."
    eval $(minikube docker-env)
fi

echo "📦 [BUILD] Building Microservices..."

docker build -t gateway-api:latest ./services/gateway-api
docker build -t risk-engine-qml:latest ./services/risk-engine-qml
docker build -t cost-analyzer:latest ./services/cost-analyzer

echo "✅ [BUILD] All images built successfully."