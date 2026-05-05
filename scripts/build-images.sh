#!/bin/bash
set -e

# If using minikube, point the docker-cli to minikube's registry
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    echo "🐳 [BUILD] Pointing Docker to Minikube registry..."
    eval $(minikube docker-env)
fi

echo "📦 [BUILD] Building Microservices..."

echo "Building Gateway API"
# 1. Generate stubs in the Risk Engine (if not already done)
# 2. Copy those stubs to the Gateway API source folder
cp services/risk-engine-qml/src/risk_engine_pb2* services/gateway-api/src/
docker build --no-cache -t gateway-api:latest ./services/gateway-api
echo "Building Risk Engine (QML)"
docker build --no-cache -t risk-engine-qml:latest ./services/risk-engine-qml
echo "Building Cost Analyzer"
docker build --no-cache -t cost-analyzer:latest ./services/cost-analyzer

echo "✅ [BUILD] All images built successfully."