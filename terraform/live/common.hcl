# Settings shared by every environment. This is the file to edit when you
# switch machines or GCP projects.
locals {
  # FILL IN (environment): the service-account key used by both the google
  # provider and the GCS state backend, and the GCP project to deploy to.
  #   export GOOGLE_CREDENTIALS_FILE=/path/to/key.json
  #   export GOOGLE_PROJECT=my-gcp-project
  credentials_file = get_env("GOOGLE_CREDENTIALS_FILE")
  project_id       = get_env("GOOGLE_PROJECT")

  # Default region for every environment. Environments can override region/zone in
  # their own inputs (dev does, to stay on the free tier). The state bucket
  # stays here either way.
  region = "europe-west4"
  zone   = "europe-west4-a"

  # Terragrunt creates this bucket on the first run if it doesn't exist.
  # Bucket names are global: change the suffix if it's taken.
  state_bucket = "${local.project_id}-marketplace-tfstate"
}
