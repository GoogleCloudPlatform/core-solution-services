locals {
  services = [
    "anthosconfigmanagement.googleapis.com", # Anthos Config Management API
    "appengine.googleapis.com",              # App Engine API
    "artifactregistry.googleapis.com",       # Artifact Registry
    "bigquery.googleapis.com",               # BigQuery
    "bigquerydatatransfer.googleapis.com",   # BigQuery Data Transfer
    "cloudbuild.googleapis.com",             # Cloud Build
    "cloudresourcemanager.googleapis.com",   # Cloud Resource manager
    "compute.googleapis.com",                # Load Balancers, Cloud Armor
    "container.googleapis.com",              # Google Kubernetes Engine
    "containerregistry.googleapis.com",      # Google Container Registry
    "dataflow.googleapis.com",               # Cloud Dataflow
    "dns.googleapis.com",                    # Cloud DNS
    "firebase.googleapis.com",               # Firebase
    "firebaseextensions.googleapis.com",     # Firebase Extension API
    "firebasehosting.googleapis.com",        # Firebase Hosting
    "firestore.googleapis.com",              # Firestore
    "gkehub.googleapis.com",                 # GKE HUB API
    "iam.googleapis.com",                    # Cloud IAM
    "iap.googleapis.com",                    # Cloud IAP
    "kgsearch.googleapis.com",               # Knowledge Graph Search API
    "language.googleapis.com",               # Natural Language API
    "logging.googleapis.com",                # Cloud Logging
    "monitoring.googleapis.com",             # Cloud Operations Suite
    "run.googleapis.com",                    # Cloud Run
    "secretmanager.googleapis.com",          # Secret Manager
    "servicenetworking.googleapis.com",      # Service Networking API
    "serviceusage.googleapis.com",           # Service Usage
    "storage.googleapis.com",                # Cloud Storage
  ]
}

# basic APIs needed to get project up and running
resource "google_project_service" "project-apis" {
  for_each                   = toset(local.services)
  project                    = var.project_id
  service                    = each.value
  disable_dependent_services = true
}

# add timer to avoid errors on new project creation and API enables
resource "time_sleep" "wait_60_seconds" {
  depends_on = [google_project_service.project-apis]
  create_duration = "60s"
}

module "terraform_runner_service_account" {
  depends_on   = [time_sleep.wait_60_seconds]
  source       = "../../modules/service_account"
  project_id   = var.project_id
  name         = "terraform-runner"
  display_name = "terraform-runner"
  description  = "Service Account for Terraform"
  roles = [
    "roles/appengine.appAdmin",
    "roles/aiplatform.admin",
    "roles/artifactregistry.admin",
    "roles/cloudbuild.builds.builder",
    "roles/cloudtrace.agent",
    "roles/compute.admin",
    "roles/container.admin",
    "roles/containerregistry.ServiceAgent",
    "roles/datastore.owner",
    "roles/editor",
    "roles/firebase.admin",
    "roles/iam.serviceAccountTokenCreator",
    "roles/iam.serviceAccountUser",
    "roles/iam.workloadIdentityUser",
    "roles/iam.workloadIdentityUser",
    "roles/logging.admin",
    "roles/logging.viewer",
    "roles/resourcemanager.projectIamAdmin",
    "roles/run.admin",
    "roles/secretmanager.secretAccessor",
    "roles/storage.admin",
  ]
}

resource "google_storage_bucket" "tfstate-bucket" {
  name                        = "${var.project_id}-tfstate"
  location                    = var.storage_multiregion
  project                     = var.project_id
  force_destroy               = false
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}
