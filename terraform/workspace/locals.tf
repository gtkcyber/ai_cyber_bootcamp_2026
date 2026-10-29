data "aws_caller_identity" "current" {}

data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  prefix = var.workspace_name
  azs    = slice(data.aws_availability_zones.available.names, 0, 2)

  # 10.x.0.0/24 public (NAT), 10.x.32.0/19 and 10.x.64.0/19 private (clusters, one per AZ)
  public_subnet   = cidrsubnet(var.vpc_cidr, 8, 0)
  private_subnets = [cidrsubnet(var.vpc_cidr, 3, 1), cidrsubnet(var.vpc_cidr, 3, 2)]
}
