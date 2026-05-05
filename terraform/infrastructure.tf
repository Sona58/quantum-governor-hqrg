# NATS Service
resource "kubernetes_service_v1" "nats_service" {
  metadata {
    name      = "nats-service"
    namespace = kubernetes_namespace_v1.hqrg.metadata[0].name
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
resource "kubernetes_deployment_v1" "nats_deployment" {
  metadata {
    name      = "nats-deployment"
    namespace = kubernetes_namespace_v1.hqrg.metadata[0].name
  }
  spec {
    replicas = 1
    selector {
      match_labels = { app = "nats" }
    }
    template {
      metadata {
        labels = { app = "nats" }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "7777"
          "prometheus.io/path"   = "/metrics"
        }
      }
      spec {
        # Container 1: The NATS Server
        container {
          name  = "nats"
          image = "nats:2.10-alpine"
          args  = ["-js", "-m", "8222"] # Enables JetStream
          port { container_port = 4222 }
          port { container_port = 8222 }
          readiness_probe {
            tcp_socket {
              port = 4222
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }
          resources {
              limits = {
                cpu    = "500m"
                memory = "512Mi"
              }
              requests = {
                cpu    = "250m"
                memory = "256Mi"
              }
          }
        }
        # Container 2: The Exporter
        container {
          name  = "nats-exporter"
          image = "natsio/prometheus-nats-exporter:latest"
          args  = [
              "-varz",
              "-jsz", "all",
              "-ri", "5",
              "http://localhost:8222"
          ]
          port { container_port = 7777 }
          liveness_probe {
            http_get {
              path = "/metrics"
              port = 7777
            }
            initial_delay_seconds = 10
            period_seconds        = 15
          }
          resources {
              limits = {
                cpu    = "500m"
                memory = "512Mi"
              }
              requests = {
                cpu    = "250m"
                memory = "256Mi"
              }
          }
        }
      }
    }
  }
}

# Redis Service
resource "kubernetes_service_v1" "redis_service" {
  metadata {
    name      = "redis-service"
    namespace = kubernetes_namespace_v1.hqrg.metadata[0].name
  }
  spec {
    selector = { app = "redis" }
    port {
      port = 6379
    }
  }
}

# Redis Deployment
resource "kubernetes_deployment_v1" "redis_deployment" {
  metadata {
    name      = "redis-deployment"
    namespace = kubernetes_namespace_v1.hqrg.metadata[0].name
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
          resources {
              limits = {
                cpu    = "500m"
                memory = "512Mi"
              }
              requests = {
                cpu    = "250m"
                memory = "256Mi"
              }
          }
        }
      }
    }
  }
}

resource "null_resource" "bootstrap_nats_stream" {
  depends_on = [kubernetes_deployment_v1.nats_deployment]

  provisioner "local-exec" {
    command = "kubectl wait --for=condition=ready pod -l app=nats -n hqrg-core --timeout=90s && kubectl run nats-bootstrap --rm -i --restart=Never --image=natsio/nats-box --namespace hqrg-core --overrides='{\"spec\":{\"containers\":[{\"name\":\"nats-bootstrap\",\"image\":\"natsio/nats-box\",\"args\":[\"nats\",\"--server=nats-service:4222\",\"str\",\"add\",\"QUANTUM\",\"--subjects\",\"quantum.*\",\"--storage\",\"file\",\"--retention\",\"limits\",\"--max-msgs=-1\",\"--max-bytes=-1\",\"--discard\",\"old\",\"--defaults\"],\"resources\":{\"limits\":{\"cpu\":\"200m\",\"memory\":\"128Mi\"},\"requests\":{\"cpu\":\"100m\",\"memory\":\"64Mi\"}}}]}}'"
  }
}