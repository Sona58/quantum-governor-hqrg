variable "ibm_quantum_token" {
  description = "Token for IBM Quantum API"
  type        = string
  sensitive   = true
}

variable "nats_url" {
  default = "nats://nats-service:4222"
}