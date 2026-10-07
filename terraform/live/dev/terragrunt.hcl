include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../modules//marketplace-vm"
}

inputs = {
  environment = "dev"

  # Always Free tier: one e2-micro in us-central1/us-east1/us-west1 and
  # 30 GB of pd-standard (boot + data together) per month.
  region = "us-central1"
  zone   = "us-central1-a"

  machine_type      = "e2-micro"
  boot_image        = "debian-cloud/debian-12"
  boot_disk_size_gb = 10
  boot_disk_type    = "pd-standard"
  data_disk_size_gb = 20
  data_disk_type    = "pd-standard"
  subnet_cidr       = "10.10.0.0/24"

  # 1 GB RAM runs Postgres + Redis + nginx + the app, so add swap and keep
  # gunicorn from spawning cpu*2+1 workers.
  swap_size_gb     = 2
  gunicorn_workers = 2

  # Ephemeral IP: it changes if the VM is stopped/started or recreated.
  static_ip = false

  # Set both to get a Let's Encrypt certificate once DNS points at the VM IP.
  domain            = ""
  letsencrypt_email = ""

  deletion_protection     = false
  snapshot_retention_days = 3
}
