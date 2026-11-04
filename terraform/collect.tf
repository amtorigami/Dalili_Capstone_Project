resource "google_storage_bucket" "landing" {
  name                        = "${local.cfg.project_id}-${local.cfg.bucket_suffix}"
  location                    = local.cfg.region
  uniform_bucket_level_access = true
  force_destroy               = true
}

resource "google_bigquery_dataset" "raw" {
  dataset_id = local.cfg.dataset_raw
  location   = local.cfg.region
}

resource "google_service_account" "collect" {
  account_id   = "dalili-collect"
  display_name = "Dalili collecte"
}

resource "google_storage_bucket_iam_member" "collect_writer" {
  bucket = google_storage_bucket.landing.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.collect.email}"
}
