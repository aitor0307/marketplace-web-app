output "public_ip" {
  value = google_compute_instance.vm.network_interface[0].access_config[0].nat_ip
}

output "instance_name" {
  value = google_compute_instance.vm.name
}

output "ssh_command" {
  value = "gcloud compute ssh ${google_compute_instance.vm.name} --zone ${var.zone} --project ${var.project_id} --tunnel-through-iap"
}

output "artifact_registry" {
  value = "${local.registry_host}/${var.project_id}/${google_artifact_registry_repository.app.repository_id}"
}

output "app_image" {
  value = local.app_image
}

output "frontend_image" {
  value = local.frontend_image
}
