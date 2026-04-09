provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_namespace" "hqrg" {
  metadata {
    name = "hqrg-core"
  }
}

# This replaces k8s/base/global-config.yaml
resource "kubernetes_config_map" "global_config" {
  metadata {
    name      = "hqrg-global-config"
    namespace = kubernetes_namespace.hqrg.metadata[0].name
  }

  data = {
    NATS_URL   = var.nats_url
    REDIS_HOST = "redis-service"
    LOG_LEVEL  = "info"
  }
}

# This replaces our dynamic secret logic in bash
resource "kubernetes_secret" "quantum_creds" {
  metadata {
    name      = "quantum-credentials"
    namespace = kubernetes_namespace.hqrg.metadata[0].name
  }

  data = {
    IBM_QUANTUM_TOKEN = var.ibm_quantum_token
  }

  type = "Opaque"
}

resource "kubernetes_resource_quota" "hqrg_quota" {
  metadata {
    name      = "hqrg-compute-quota"
    namespace = kubernetes_namespace.hqrg.metadata[0].name
  }
  spec {
    hard = {
      "requests.cpu"    = "4"
      "requests.memory" = "8Gi"
      "limits.cpu"      = "8"
      "limits.memory"   = "16Gi"
    }
  }
}