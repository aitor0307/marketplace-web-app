# Root Terragrunt config, included by every environment under live/.
locals {
  common = read_terragrunt_config("${get_parent_terragrunt_dir()}/common.hcl").locals
}

remote_state {
  backend = "gcs"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    project     = local.common.project_id
    location    = local.common.region
    bucket      = local.common.state_bucket
    prefix      = "marketplace/${path_relative_to_include()}"
    credentials = local.common.credentials_file
  }
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "google" {
  project     = "${local.common.project_id}"
  region      = "${local.common.region}"
  zone        = "${local.common.zone}"
  credentials = "${local.common.credentials_file}"
}
EOF
}

inputs = {
  project_id = local.common.project_id
  region     = local.common.region
  zone       = local.common.zone
}
