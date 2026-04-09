#!/bin/bash
set -e

echo "🌊 [INFRA] Bootstrapping NATS JetStream..."

# Apply NATS manifests
kubectl apply -f k8s/infrastructure/nats-setup.yaml

# Wait for NATS to be ready before configuring streams
echo "⏳ Waiting for NATS pod..."
kubectl wait --for=condition=ready pod -l app=nats --timeout=90s

# Create the JetStream 'QUANTUM' stream
# We use 'kubectl exec' to run the nats-cli inside the container
kubectl exec -it deployment/nats-deployment -- \
  nats str add QUANTUM \
  --subjects "quantum.*" \
  --storage file \
  --retention limits \
  --max-msgs=-1 \
  --max-bytes=-1 \
  --discard old

echo "✅ [INFRA] NATS JetStream configured."