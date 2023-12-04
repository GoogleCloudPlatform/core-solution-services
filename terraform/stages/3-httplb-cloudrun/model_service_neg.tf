resource "google_compute_region_network_endpoint_group" "model_service_neg" {
  name                  = "model-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  cloud_run {
    service = "model"
  }
}
