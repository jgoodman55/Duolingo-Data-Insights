variable "credentials" {
  description = "My Credentials File Path"
  default     = "C:/gcp/duolingo-data-insights-4efdf9b8abdc.json"
}

variable "project" {
  description = "Project"
  default     = "duolingo-data-insights"
}

variable "location" {
  description = "Project Location"
  default     = "US"
}

variable "region" {
  description = "Project Region"
  default     = "us-central1"
}

variable "gcs_raw_bucket_name" {
  description = "Raw Duolingo Spaced Repitition Data"
  default     = "duolingo-raw-bucket"
}

variable "bq_dataset_name" {
  description = "My BigQuery dataset name"
  default     = "duolingo_data_insights_dataset"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}