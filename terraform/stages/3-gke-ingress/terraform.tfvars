project_id                = "your-project-id" # sb-var:project_id
region                    = "us-central1"     # sb-var:gcp_region
cluster_name              = "main-cluster"
cluster_external_endpoint = ""                # sb-var:cluster_external_endpoint
cluster_ca_certificate    = ""                # sb-var:cluster_ca_certificate
managed_cert_name         = "managed-cert"
frontend_config_name      = "default-frontend-config"
domains                   = [
  "example.com" # sb-var:domain_name
]
