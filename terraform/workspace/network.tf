module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "6.7.2"

  name = local.prefix
  cidr = var.vpc_cidr
  azs  = local.azs

  public_subnets  = [local.public_subnet]
  private_subnets = local.private_subnets

  enable_dns_hostnames = true
  enable_dns_support   = true
  create_igw           = true
  enable_nat_gateway   = true
  single_nat_gateway   = true

  # The module locks down the VPC default security group; Databricks gets its own below.
  manage_default_security_group = true
}

# Databricks cluster security group: all traffic within the group, all egress.
resource "aws_security_group" "databricks" {
  name        = "${local.prefix}-databricks"
  description = "Databricks classic compute"
  vpc_id      = module.vpc.vpc_id

  tags = { Name = "${local.prefix}-databricks" }
}

resource "aws_vpc_security_group_ingress_rule" "databricks_self_tcp" {
  security_group_id            = aws_security_group.databricks.id
  referenced_security_group_id = aws_security_group.databricks.id
  ip_protocol                  = "tcp"
  from_port                    = 0
  to_port                      = 65535
  description                  = "Intra-cluster TCP"
}

resource "aws_vpc_security_group_ingress_rule" "databricks_self_udp" {
  security_group_id            = aws_security_group.databricks.id
  referenced_security_group_id = aws_security_group.databricks.id
  ip_protocol                  = "udp"
  from_port                    = 0
  to_port                      = 65535
  description                  = "Intra-cluster UDP"
}

resource "aws_vpc_security_group_egress_rule" "databricks_all" {
  security_group_id = aws_security_group.databricks.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
  description       = "All egress (control plane, S3, metastore, PyPI)"
}

# S3 stays on the AWS backbone instead of the NAT. Gateway endpoints are free.
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = module.vpc.vpc_id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = concat(module.vpc.private_route_table_ids, module.vpc.public_route_table_ids)

  tags = { Name = "${local.prefix}-s3" }
}

resource "aws_vpc_endpoint" "interface" {
  for_each = var.enable_interface_endpoints ? toset(["sts", "kinesis-streams"]) : toset([])

  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.${each.key}"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = module.vpc.private_subnets
  security_group_ids  = [aws_security_group.databricks.id]
  private_dns_enabled = true

  tags = { Name = "${local.prefix}-${each.key}" }
}

resource "databricks_mws_networks" "this" {
  provider = databricks.mws

  account_id         = var.databricks_account_id
  network_name       = "${local.prefix}-network"
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnets
  security_group_ids = [aws_security_group.databricks.id]
}
