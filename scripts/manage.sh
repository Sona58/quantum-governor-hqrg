#!/bin/bash

case "$1" in
  "deploy")
    cd terraform
    terraform init
    # Pass the .env variable into terraform
    terraform apply -var="ibm_quantum_token=$IBM_QUANTUM_TOKEN" -auto-approve
    ;;
  "destroy")
    cd terraform
    terraform destroy -var="ibm_quantum_token=$IBM_QUANTUM_TOKEN" -auto-approve
    ;;
esac