locals {
  name           = "marketplace-${var.environment}"
  data_disk_name = "data"
  registry_host  = "${var.region}-docker.pkg.dev"
  registry_repo  = "${local.registry_host}/${var.project_id}/${google_artifact_registry_repository.app.repository_id}"
  app_image      = var.app_image != "" ? var.app_image : "${local.registry_repo}/app:latest"
  frontend_image = var.frontend_image != "" ? var.frontend_image : "${local.registry_repo}/frontend:latest"

  nginx_conf = templatefile("${path.module}/templates/nginx.conf.tftpl", {
    server_name = var.domain != "" ? var.domain : "_"
    app_port      = var.app_port
    frontend_port = var.frontend_port
  })

  docker_compose = templatefile("${path.module}/templates/docker-compose.yml.tftpl", {
    app_image        = local.app_image
    app_port         = var.app_port
    gunicorn_workers = var.gunicorn_workers
    frontend_image   = local.frontend_image
    frontend_port    = var.frontend_port
  })

  startup_script = templatefile("${path.module}/templates/startup.sh.tftpl", {
    data_disk_name    = local.data_disk_name
    swap_size_gb      = var.swap_size_gb
    postgres_db       = var.postgres_db
    postgres_user     = var.postgres_user
    registry_host     = local.registry_host
    domain            = var.domain
    letsencrypt_email = var.letsencrypt_email
    nginx_conf        = local.nginx_conf
    docker_compose    = local.docker_compose
  })
}

# APIs are left enabled on destroy: they're project-wide and shared by both envs.
resource "google_project_service" "services" {
  for_each = toset(["compute.googleapis.com", "artifactregistry.googleapis.com"])

  service            = each.key
  disable_on_destroy = false
}

# --- Network -----------------------------------------------------------------

resource "google_compute_network" "vpc" {
  name                    = "${local.name}-vpc"
  auto_create_subnetworks = false

  depends_on = [google_project_service.services]
}

resource "google_compute_subnetwork" "subnet" {
  name          = "${local.name}-subnet"
  network       = google_compute_network.vpc.id
  region        = var.region
  ip_cidr_range = var.subnet_cidr
}

# Only 80/443 are public. Postgres (5432) and Redis never get a rule, so
# they stay unreachable from outside the VM.
resource "google_compute_firewall" "web" {
  name          = "${local.name}-allow-web"
  network       = google_compute_network.vpc.id
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["${local.name}-web"]

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }
}

resource "google_compute_firewall" "ssh" {
  name          = "${local.name}-allow-ssh"
  network       = google_compute_network.vpc.id
  source_ranges = var.ssh_source_ranges
  target_tags   = ["${local.name}-web"]

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}

resource "google_compute_address" "public" {
  count = var.static_ip ? 1 : 0

  name   = "${local.name}-ip"
  region = var.region

  depends_on = [google_project_service.services]
}

# --- Container registry ------------------------------------------------------

resource "google_artifact_registry_repository" "app" {
  repository_id = local.name
  location      = var.region
  format        = "DOCKER"

  depends_on = [google_project_service.services]
}

# --- VM identity -------------------------------------------------------------

resource "google_service_account" "vm" {
  account_id   = "${local.name}-vm"
  display_name = "Marketplace ${var.environment} VM"
}

resource "google_project_iam_member" "vm" {
  for_each = toset(["roles/logging.logWriter", "roles/monitoring.metricWriter"])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.vm.email}"
}

resource "google_artifact_registry_repository_iam_member" "vm_reader" {
  repository = google_artifact_registry_repository.app.name
  location   = var.region
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.vm.email}"
}

# --- Storage -----------------------------------------------------------------

resource "google_compute_disk" "data" {
  name = "${local.name}-data"
  type = var.data_disk_type
  zone = var.zone
  size = var.data_disk_size_gb

  depends_on = [google_project_service.services]
}

resource "google_compute_resource_policy" "data_snapshots" {
  name   = "${local.name}-data-snapshots"
  region = var.region

  snapshot_schedule_policy {
    schedule {
      daily_schedule {
        days_in_cycle = 1
        start_time    = "03:00"
      }
    }
    retention_policy {
      max_retention_days    = var.snapshot_retention_days
      on_source_disk_delete = "KEEP_AUTO_SNAPSHOTS"
    }
  }
}

resource "google_compute_disk_resource_policy_attachment" "data_snapshots" {
  name = google_compute_resource_policy.data_snapshots.name
  disk = google_compute_disk.data.name
  zone = var.zone
}

# --- VM ----------------------------------------------------------------------

resource "google_compute_instance" "vm" {
  name                      = "${local.name}-vm"
  machine_type              = var.machine_type
  zone                      = var.zone
  tags                      = ["${local.name}-web"]
  deletion_protection       = var.deletion_protection
  allow_stopping_for_update = true

  boot_disk {
    initialize_params {
      image = var.boot_image
      size  = var.boot_disk_size_gb
      type  = var.boot_disk_type
    }
  }

  attached_disk {
    source      = google_compute_disk.data.id
    device_name = local.data_disk_name
  }

  network_interface {
    subnetwork = google_compute_subnetwork.subnet.id
    # With static_ip = false, nat_ip is null and GCP assigns an ephemeral IP.
    access_config {
      nat_ip = var.static_ip ? google_compute_address.public[0].address : null
    }
  }

  service_account {
    email  = google_service_account.vm.email
    scopes = ["cloud-platform"]
  }

  shielded_instance_config {
    enable_secure_boot          = true
    enable_vtpm                 = true
    enable_integrity_monitoring = true
  }

  # Set through `metadata` rather than `metadata_startup_script` so that
  # changing the script updates it in place instead of recreating the VM.
  # The new script runs on the next boot.
  metadata = {
    startup-script = local.startup_script
    enable-oslogin = "TRUE"
  }

  lifecycle {
    # A newer image in the family shouldn't force a rebuild.
    ignore_changes = [boot_disk[0].initialize_params[0].image]
  }
}
