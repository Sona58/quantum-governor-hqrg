# NATS Service
resource "kubernetes_service" "nats_service" {
  metadata {
    name      = "nats-service"
    namespace = kubernetes_namespace.hqrg.metadata[0].name
  }
  spec {
    selector = { app = "nats" }
    port {
      name = "client"
      port = 4222
    }
  }
}

# NATS Deployment with JetStream enabled
resource "kubernetes_deployment" "nats_deployment" {
  metadata {
    name      = "nats-deployment"
    namespace = kubernetes_namespace.hqrg.metadata[0].name
  }
  spec {
    replicas = 1
    selector {
      match_labels = { app = "nats" }
    }
    template {
      metadata {
        labels = { app = "nats" }
      }
      spec {
        container {
          name  = "nats"
          image = "nats:2.10-alpine"
          args  = ["-js"] # Enables JetStream
          port {
            container_port = 4222
          }
        }
      }
    }
  }
}

# Redis Service
resource "kubernetes_service" "redis_service" {
  metadata {
    name      = "redis-service"
    namespace = kubernetes_namespace.hqrg.metadata[0].name
  }
  spec {
    selector = { app = "redis" }
    port {
      port = 6379
    }
  }
}

# Redis Deployment
resource "kubernetes_deployment" "redis_deployment" {
  metadata {
    name      = "redis-deployment"
    namespace = kubernetes_namespace.hqrg.metadata[0].name
  }
  spec {
    replicas = 1
    selector {
      match_labels = { app = "redis" }
    }
    template {
      metadata {
        labels = { app = "redis" }
      }
      spec {
        container {
          name  = "redis"
          image = "redis:alpine"
          port {
            container_port = 6379
          }
        }
      }
    }
  }
}

resource "null_resource" "bootstrap_nats_stream" {
  # This ensures we only run this AFTER the NATS deployment is ready
  depends_on = [kubernetes_deployment.nats_deployment]

  provisioner "local-exec" {
    command = <<EOT
      kubectl wait --for=condition=ready pod -l app=nats -n ${kubernetes_namespace.hqrg.metadata[0].name} --timeout=90s
      kubectl exec -n ${kubernetes_namespace.hqrg.metadata[0].name} deployment/nats-deployment -- nats str add QUANTUM --subjects "quantum.*" --storage file --retention limits --max-msgs=-1 --max-bytes=-1 --discard old
    EOT
  }
}