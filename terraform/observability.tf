# Prometheus Deployment to scrape metrics from Gateway and Executors
resource "kubernetes_deployment_v1" "prometheus" {
  metadata {
    name      = "prometheus"
    namespace = kubernetes_namespace_v1.hqrg.metadata[0].name
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
          args  = ["--config.file=/etc/prometheus/prometheus.yml"]
          
          volume_mount {
              name       = "config-volume"
              mount_path = "/etc/prometheus"
          }
        
          port { container_port = 9090 }
          
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
        volume {
            name = "config-volume"
            config_map {
              name = "prometheus-server-conf"
            }
        }
      }
    }
  }
}

# Service to access the Grafana Dashboard
resource "kubernetes_service_v1" "grafana" {
  metadata {
    name      = "grafana-service"
    namespace = kubernetes_namespace_v1.hqrg.metadata[0].name
  }
  spec {
    selector = { app = "grafana" } # This must match the label in your deployment
    port {
      port        = 3000
      target_port = 3000
    }
    type = "NodePort"
  }
}

# Prometheus Deployment
resource "kubernetes_deployment_v1" "grafana" {
  metadata {
    name      = "grafana"
    namespace = kubernetes_namespace_v1.hqrg.metadata[0].name
  }
  spec {
    replicas = 1
    selector {
        match_labels = { app = "grafana" }
    }
    template {
        metadata {
            labels = { app = "grafana" }
        }
        spec {
            container {
                name = "grafana"
                image = "grafana/grafana:latest"
                port {
                    container_port = 3000
                }
                volume_mount {
                    name       = "datasource-volume"
                    mount_path = "/etc/grafana/provisioning/datasources"
                    read_only  = true
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
            volume {
              name = "datasource-volume"
              config_map {
                name = "grafana-datasources"
              }
            }
        }
    }
  }
}

# Connection bridge between Grafana and Prometheus
resource "kubernetes_service_v1" "prometheus" {
  metadata {
    name      = "prometheus"
    namespace = kubernetes_namespace_v1.hqrg.metadata[0].name
  }
  spec {
    selector = { app = "prometheus" } # Must match the label in your Prometheus deployment
    port {
      port        = 9090
      target_port = 9090
    }
    type = "ClusterIP" # Internal only, which is perfect for pod-to-pod talk
  }
}

resource "kubernetes_config_map_v1" "prometheus_config" {
  metadata {
    name      = "prometheus-server-conf"
    namespace = kubernetes_namespace_v1.hqrg.metadata[0].name
  }

  data = {
    "prometheus.yml" = <<EOF
global:
  scrape_interval: 5s
scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      # This looks for the annotation "prometheus.io/scrape: true"
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      # This handles custom paths like /jsz or /varz
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      # This tells Prometheus which port to hit
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        replacement: $1:$2
        regex: ([^:]+)(?::\d+)?;(\d+)
EOF
  }
}

resource "kubernetes_cluster_role_v1" "prometheus" {
  metadata { name = "prometheus-role" }
  rule {
    api_groups = [""]
    resources  = ["pods", "nodes", "nodes/proxy", "services", "endpoints", "configmaps"]
    verbs      = ["get", "list", "watch"]
  }
}

resource "kubernetes_cluster_role_binding_v1" "prometheus" {
  metadata { name = "prometheus-binding" }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role_v1.prometheus.metadata[0].name
  }
  subject {
    kind      = "ServiceAccount"
    name      = "default"
    namespace = kubernetes_namespace_v1.hqrg.metadata[0].name
  }
}

# ConfigMap for the Data Source
resource "kubernetes_config_map_v1" "grafana_datasources" {
  metadata {
    name      = "grafana-datasources"
    namespace = kubernetes_namespace_v1.hqrg.metadata[0].name
  }

  data = {
    "prometheus.yaml" = <<EOF
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    isDefault: true
EOF
  }
}