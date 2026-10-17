variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "zone" {
  type = string
}

variable "environment" {
  description = "Environment name (dev, prod); prefixes every resource name."
  type        = string
}

variable "machine_type" {
  type    = string
  default = "e2-small"
}

variable "boot_image" {
  type    = string
  default = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"
}

variable "boot_disk_size_gb" {
  type    = number
  default = 20
}

variable "boot_disk_type" {
  type    = string
  default = "pd-balanced"
}

variable "swap_size_gb" {
  description = "Swap file on the boot disk; worth it on e2-micro (1 GB RAM). 0 = none."
  type        = number
  default     = 0
}

variable "gunicorn_workers" {
  description = "Overrides the image's cpu*2+1 gunicorn workers. 0 = keep the image default."
  type        = number
  default     = 0
}

variable "static_ip" {
  description = "Reserve a static external IP. false = ephemeral IP, which changes when the VM is stopped/started or recreated."
  type        = bool
  default     = true
}

variable "data_disk_size_gb" {
  description = "Persistent disk holding Postgres data, Docker volumes and app secrets; it outlives the VM."
  type        = number
  default     = 20
}

variable "data_disk_type" {
  type    = string
  default = "pd-balanced"
}

variable "subnet_cidr" {
  type = string
}

variable "ssh_source_ranges" {
  description = "CIDRs allowed to reach port 22. The default is Google's IAP range, so SSH only works through `gcloud compute ssh --tunnel-through-iap`."
  type        = list(string)
  default     = ["35.235.240.0/20"]
}

variable "domain" {
  description = "Public hostname nginx serves. Empty = serve any host over plain HTTP."
  type        = string
  default     = ""
}

variable "letsencrypt_email" {
  description = "With domain set, certbot requests a certificate at boot. Empty = no TLS."
  type        = string
  default     = ""
}

variable "app_image" {
  description = "Full image reference for the app container. Empty = <this env's Artifact Registry repo>/app:latest."
  type        = string
  default     = ""
}

variable "frontend_image" {
  description = "Full image reference for the React frontend container. Empty = <this env's Artifact Registry repo>/frontend:latest."
  type        = string
  default     = ""
}

variable "frontend_port" {
  description = "Host port (bound to 127.0.0.1) nginx proxies the SPA to."
  type        = number
  default     = 8080
}

variable "app_port" {
  description = "Host port (bound to 127.0.0.1) nginx proxies to."
  type        = number
  default     = 8000
}

variable "postgres_db" {
  type    = string
  default = "marketplace"
}

variable "postgres_user" {
  type    = string
  default = "marketplace"
}

variable "deletion_protection" {
  type    = bool
  default = false
}

variable "snapshot_retention_days" {
  description = "Daily snapshots of the data disk are kept this many days."
  type        = number
  default     = 7
}
