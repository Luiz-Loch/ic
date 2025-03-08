terraform {
  required_version = ">=1.10.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.85.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      "managed-by" = "terraform",
      "projec"     = "ic",
    }
  }
}

locals {
  name = "tf-ic"
  region = "us-east-1"
}