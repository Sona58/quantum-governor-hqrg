# 2. Cost Analyzer Deployment
resource "kubernetes_deployment_v1" "cost_analyzer" {
  metadata {
    name      = "cost-analyzer"
    namespace = kubernetes_namespace_v1.hqrg.metadata[0].name
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
          name              = "cost-analyzer"
          image             = "cost-analyzer:latest"
          image_pull_policy = "Never"

          env_from {
            config_map_ref {
              name = kubernetes_config_map_v1.global_config.metadata[0].name
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