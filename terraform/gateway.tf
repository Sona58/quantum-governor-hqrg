resource "kubernetes_deployment" "gateway_api" {
  metadata {
    name      = "gateway-api"
    namespace = kubernetes_namespace.hqrg.metadata[0].name
  }

  spec {
    replicas = 2
    selector {
      match_labels = { app = "gateway-api" }
    }

    template {
      metadata {
        labels = { app = "gateway-api" }
      }

      spec {
        container {
          name  = "gateway-api"
          image = "gateway-api:latest"
          image_pull_policy = "Never"

          env_from {
            config_map_ref {
              name = kubernetes_config_map.global_config.metadata[0].name
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

resource "kubernetes_service" "gateway_service" {
  metadata {
    name      = "gateway-api-service"
    namespace = kubernetes_namespace.hqrg.metadata[0].name
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