resource "kubernetes_deployment" "cost_analyzer" {
  metadata {
    name      = "cost-analyzer"
    namespace = kubernetes_namespace.hqrg.metadata[0].name
  }

  spec {
    replicas = 1
    selector {
      match_labels = { app = "cost-analyzer" }
    }

    template {
      metadata {
        labels = { app = "cost-analyzer" }
      }

      spec {
        container {
          name  = "cost-analyzer"
          image = "cost-analyzer:latest"
          image_pull_policy = "Never"

          # Shared logic from main.tf
          env_from {
            config_map_ref {
              name = kubernetes_config_map.global_config.metadata[0].name
            }
          }

          resources {
            limits = {
              cpu    = "200m"
              memory = "128Mi"
            }
            requests = {
              cpu    = "100m"
              memory = "64Mi"
            }
          }
        }
      }
    }
  }
}