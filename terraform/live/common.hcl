# Settings shared by every environment. This is the file to edit when you
# switch machines or GCP projects.
locals {
  # Service-account key used by both the google provider and the GCS state
  # backend. Override per machine without editing this file:
  #   export GOOGLE_CREDENTIALS_FILE=/path/to/other-key.json
  credentials_file = get_env("GOOGLE_CREDENTIALS_FILE", "/home/aitor/.cloudkeys/ceva-cloud-0b01989bd8b6.json")

  project_id = get_env("GOOGLE_PROJECT", "ceva-cloud")

  # europe-west4 (Netherlands) mirrors the Azure "West Europe" region the
  # rest of the stack runs in. Environments can override region/zone in
  # their own inputs (dev does, to stay on the free tier). The state bucket
  # stays here either way.
  region = "europe-west4"
  zone   = "europe-west4-a"

  # Terragrunt creates this bucket on the first run if it doesn't exist.
  state_bucket = "ceva-cloud-marketplace-tfstate"
}
