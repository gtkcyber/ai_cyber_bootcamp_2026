terraform {
  required_version = "~> 1.16"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.62"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.130"
    }
    time = {
      source  = "hashicorp/time"
      version = ">= 0.13"
    }
  }

  backend "s3" {
    bucket       = "<YOUR-TFSTATE-BUCKET>"
    key          = "databricks/bootcamp.tfstate"
    region       = "us-east-1"
    profile      = "gtk-cyber"
    encrypt      = true
    use_lockfile = true
  }
}
