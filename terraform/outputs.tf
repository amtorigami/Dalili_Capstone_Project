output "landing_bucket" {
  value = google_storage_bucket.landing.name
}

output "datasets" {
  value = [
    google_bigquery_dataset.raw.dataset_id,
    google_bigquery_dataset.curated.dataset_id,
    google_bigquery_dataset.marts.dataset_id,
    google_bigquery_dataset.snapshots.dataset_id,
  ]
}
