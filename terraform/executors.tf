# 1. Risk Engine Deployment
resource "kubernetes_deployment_v1" "risk_engine" {
  metadata {
    name      = "risk-engine-qml"
    namespace = kubernetes_namespace_v1.hqrg.metadata[0].name
  }

  spec {
    replicas = 1
    selector {
      match_labels = { app = "risk-engine-qml" }
    }

    template {
      metadata {
        labels = { app = "risk-engine-qml" }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "8000"
          "prometheus.io/path"   = "/metrics"
        }
      }

      spec {
        container {
          name              = "risk-engine"
          image             = "risk-engine-qml:latest"
          image_pull_policy = "Never" # Uses images from local build-images.sh script
          
          # Expose gRPC port for direct Gateway communication
          port {
              name          = "grpc"
              container_port= 50051
          }
          
          # Keep Prometheus metrics port exposed
          port {
              name          = "metrics"
              container_port= 8000
          }

          # Inherit shared variables like NATS_URL and REDIS_HOST
          env_from {
            config_map_ref {
              name = kubernetes_config_map_v1.global_config.metadata[0].name
            }
          }

          # Specific variables for Quantum execution logic
          env {
            name  = "ENGINE_TYPE"
            value = "ibm-qpu"
          }

          # Securely inject the IBM Token from the Secret
          env {
            name = "IBM_QUANTUM_TOKEN"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.quantum_creds.metadata[0].name
                key  = "IBM_QUANTUM_TOKEN"
              }
            }
          }

          # Resource constraints for Qiskit Aer simulation [cite: 9]
          resources {
            limits = {
              cpu    = "1"      # Allow up to 1 full core for circuit simulation [cite: 9]
              memory = "2Gi"    # Quantum simulations are memory intensive [cite: 9]
            }
            requests = {
              cpu    = "500m"
              memory = "1Gi"
            }
          }
        }
      }
    }
  }
}

# Internal Service for gRPC Discovery
# This allows the Gateway to use 'risk-engine-service:50051' as the host
resource "kubernetes_service_v1" "risk_engine_service" {
    metadata {
        name                = "risk-engine-service"
        namespace           = kubernetes_namespace_v1.hqrg.metadata[0].name
    }
    
    spec {
        selector = {
            app             = "risk-engine-qml"
        }
        
        port {
            name            = "grpc"
            port            = 50051
            target_port     = 50051
        }
        
        type                = "ClusterIP"
    }
}