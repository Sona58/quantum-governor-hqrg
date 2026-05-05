output "gateway_url" {
  value       = "http://gateway-api-service.${kubernetes_namespace_v1.hqrg.metadata[0].name}.svc.cluster.local"
  description = "Internal URL for the Gateway API"
}