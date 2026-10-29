provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = var.tags
  }
}

# Account-level ("MWS") provider. Auth comes from the gtk-account profile in ~/.databrickscfg:
# account host, account id, and the OAuth M2M credentials of the automation service principal.
provider "databricks" {
  alias   = "mws"
  profile = var.account_profile
}
