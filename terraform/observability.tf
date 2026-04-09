# Prometheus Deployment to scrape metrics from Gateway and Executors
resource "kubernetes_deployment" "prometheus" {
  metadata {
    name      = "prometheus"
    namespace = kubernetes_namespace.hqrg.metadata[0].name
  }
  spec {
    replicas = 1
    selector {
      match_labels = { app = "prometheus" }
    }
    template {
      metadata {
        labels = { app = "prometheus" }
      }
      spec {
        container {
          name  = "prometheus"
          image = "prom/prometheus:latest"
          port { container_port = 9090 }
        }
      }
    }
  }
}

# Service to access the Grafana Dashboard
resource "kubernetes_service" "grafana" {
  metadata {
    name      = "grafana-service"
    namespace = kubernetes_namespace.hqrg.metadata[0].name
  }
  spec {
    selector = { app = "grafana" }
    port {
      port        = 3000
      target_port = 3000
    }
    type = "NodePort" # Allows you to access it via your browser
  }
}