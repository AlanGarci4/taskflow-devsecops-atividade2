terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Justificativas de excecao do lab para os skips aplicados no CI (Checkov):
# - CKV2_AWS_61: ambiente didatico sem integração de evento S3 com Lambda.
# - CKV_AWS_145: o lab usa criptografia SSE-S3 (AES256), sem KMS gerenciado.
# - CKV_AWS_144: sem replicacao cross-region por custo e escopo da atividade.
# - CKV2_AWS_5: SG isolado para demonstracao, sem acoplamento a recurso computacional.
# - CKV2_AWS_62: sem notificacoes S3 para SNS/SQS no escopo deste exercicio.
# - CKV_AWS_382: bucket de logs com acesso publico bloqueado e uso interno de auditoria.
# - CKV_AWS_23: regra de egress ampla mantida para simplicidade do laboratorio.

variable "aws_region" {
  type        = string
  description = "Regiao AWS"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Nome do projeto"
  default     = "taskflow"
}

variable "allowed_ip_cidr" {
  type        = string
  description = "IP/CIDR autorizado para acesso administrativo"
  default     = "203.0.113.10/32"
}

resource "aws_s3_bucket" "logs" {
  bucket = "${var.project_name}-logs-bucket-demo"

  tags = {
    Project = var.project_name
    Env     = "lab"
    Owner   = "devsecops"
  }
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_logging" "logs" {
  bucket        = aws_s3_bucket.logs.id
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "audit/"
}

resource "aws_security_group" "app" {
  name        = "${var.project_name}-app-sg"
  description = "Security group da app"

  ingress {
    description = "Acesso SSH restrito"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ip_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-app-sg"
  }
}
