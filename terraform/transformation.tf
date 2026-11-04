resource "google_bigquery_dataset" "curated" {
  dataset_id = local.cfg.dataset_curated
  location   = local.cfg.region
}

resource "google_bigquery_dataset" "marts" {
  dataset_id = local.cfg.dataset_marts
  location   = local.cfg.region
}

resource "google_bigquery_dataset" "snapshots" {
  dataset_id = local.cfg.dataset_snapshots
  location   = local.cfg.region
}

resource "google_service_account" "dbt" {
  account_id   = "dalili-dbt"
  display_name = "Dalili dbt"
}

resource "google_project_iam_member" "dbt_editor" {
  project = local.cfg.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.dbt.email}"
}

resource "google_project_iam_member" "dbt_jobs" {
  project = local.cfg.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.dbt.email}"
}
