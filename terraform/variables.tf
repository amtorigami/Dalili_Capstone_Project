locals {
  cfg = yamldecode(file("${path.module}/../collect/config/gcp_config.yaml"))
}
