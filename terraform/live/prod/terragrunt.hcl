include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../modules//marketplace-vm"
}

inputs = {
  environment = "prod"

  machine_type      = "e2-standard-2"
  boot_disk_size_gb = 30
  data_disk_size_gb = 50
  data_disk_type    = "pd-ssd"
  subnet_cidr       = "10.20.0.0/24"

  # Set both to get a Let's Encrypt certificate once DNS points at the VM IP.
  domain            = ""
  letsencrypt_email = ""

  deletion_protection     = true
  snapshot_retention_days = 14
}
