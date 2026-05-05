resource "kubernetes_deployment_v1" "gateway_api" {
  metadata {
    name      = "gateway-api"
    namespace = kubernetes_namespace_v1.hqrg.metadata[0].name
  }

  spec {
    replicas = 2
    selector {
      match_labels = { app = "gateway-api" }
    }

    template {
      metadata {
        labels = { app = "gateway-api" }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "8000"
          "prometheus.io/path"   = "/metrics/"
        }
      }

      spec {
        container {
          name  = "gateway-api"
          image = "gateway-api:latest"
          image_pull_policy = "Never"
          
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

          env_from {
            config_map_ref {
              name = kubernetes_config_map_v1.global_config.metadata[0].name
            }
          }

          port {
            container_port = 8000
          }

          readiness_probe {
            http_get {
              path = "/docs"
              port = 8000
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }
        }
      }
    }
  }
}

resource "kubernetes_service_v1" "gateway_service" {
  metadata {
    name      = "gateway-api-service"
    namespace = kubernetes_namespace_v1.hqrg.metadata[0].name
  }
  spec {
    selector = { app = "gateway-api" }
    port {
      port        = 80
      target_port = 8000
    }
    type = "ClusterIP"
  }
}