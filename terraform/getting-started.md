# Terraform Getting Started

A practical introduction to Terraform fundamentals — providers, resources, variables, outputs, and state management — with annotated examples.

---

## Table of Contents

- [What is Terraform?](#what-is-terraform)
- [Core Workflow](#core-workflow)
- [Providers](#providers)
- [Resources](#resources)
- [Variables](#variables)
- [Outputs](#outputs)
- [Data Sources](#data-sources)
- [State Management](#state-management)
- [Best Practices](#best-practices)
- [Project Structure](#project-structure)

---

## What is Terraform?

Terraform is an Infrastructure as Code (IaC) tool that lets you define cloud and on-premises resources in human-readable configuration files that you can version, reuse, and share.

```mermaid
graph LR
    A[Write HCL Code] --> B[terraform init]
    B --> C[terraform plan]
    C --> D[Review Changes]
    D --> E[terraform apply]
    E --> F[Infrastructure Created]
    F --> G[terraform destroy]

    style A fill:#7b68ee,color:#fff
    style E fill:#27ae60,color:#fff
    style G fill:#e74c3c,color:#fff
```

---

## Core Workflow

```bash
# 1. Initialize — download providers and modules
terraform init

# 2. Format — standardize code formatting
terraform fmt

# 3. Validate — check syntax and configuration
terraform validate

# 4. Plan — preview changes before applying
terraform plan

# 5. Apply — create/update infrastructure
terraform apply

# 6. Destroy — tear down all managed resources
terraform destroy
```

### Key Flags

```bash
terraform plan -out=plan.tfplan    # Save plan to file
terraform apply plan.tfplan         # Apply saved plan (no confirmation prompt)
terraform apply -auto-approve       # Skip confirmation (CI/CD pipelines)
terraform destroy -target=aws_instance.web  # Destroy specific resource
terraform state list                # List resources in state
terraform state show aws_instance.web       # Show resource details
```

---

## Providers

Providers are plugins that let Terraform interact with cloud platforms and services.

### AWS Provider

```hcl
# Configure the AWS provider
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"     # Allow 5.x updates, not 6.0
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "devops-lab"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
```

### Multiple Provider Configurations

```hcl
# Default provider (us-east-1)
provider "aws" {
  region = "us-east-1"
}

# Additional provider for another region
provider "aws" {
  alias  = "eu"
  region = "eu-west-1"
}

# Use aliased provider
resource "aws_s3_bucket" "eu_bucket" {
  provider = aws.eu
  bucket   = "my-eu-bucket"
}
```

---

## Resources

Resources are the most important element in Terraform. Each resource block describes one or more infrastructure objects.

### EC2 Instance

```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"   # Amazon Linux 2
  instance_type = var.instance_type

  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.web.id]
  key_name               = aws_key_pair.deployer.key_name

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name = "${var.project}-web-server"
  }
}
```

### S3 Bucket

```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "${var.project}-logs-${var.environment}"

  tags = {
    Name = "Application Logs"
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
      sse_algorithm = "aws:kms"
    }
  }
}
```

### VPC

```hcl
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.project}-vpc"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project}-public-subnet"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project}-igw"
  }
}
```

---

## Variables

### Defining Variables

```hcl
# variables.tf

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "project" {
  description = "Project name for resource tagging"
  type        = string
  default     = "devops-lab"
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the web server"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "extra_tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}
```

### Setting Variable Values

```bash
# 1. terraform.tfvars (auto-loaded)
# terraform.tfvars
aws_region    = "us-west-2"
environment   = "staging"
instance_type = "t3.small"

# 2. Command line
terraform apply -var="environment=prod"

# 3. Environment variables
export TF_VAR_environment="prod"

# 4. .auto.tfvars files (auto-loaded, alphabetical)
# prod.auto.tfvars
environment   = "prod"
instance_type = "t3.medium"
```

### Variable Types

| Type | Example | Description |
|------|---------|-------------|
| `string` | `"us-east-1"` | Single text value |
| `number` | `3` | Numeric value |
| `bool` | `true` | Boolean |
| `list(string)` | `["a", "b"]` | Ordered collection |
| `map(string)` | `{key = "val"}` | Key-value pairs |
| `object({...})` | Complex structure | Structured data |

---

## Outputs

Outputs expose values after `terraform apply` — useful for passing data between modules or displaying results.

```hcl
# outputs.tf

output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.web.id
}

output "instance_public_ip" {
  description = "Public IP address of the web server"
  value       = aws_instance.web.public_ip
}

output "s3_bucket_arn" {
  description = "ARN of the logs S3 bucket"
  value       = aws_s3_bucket.logs.arn
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

# Sensitive output (hidden in CLI output)
output "db_connection_string" {
  description = "Database connection string"
  value       = "postgres://${var.db_user}:${var.db_password}@${aws_db_instance.main.endpoint}/${var.db_name}"
  sensitive   = true
}
```

```bash
# View all outputs
terraform output

# View specific output
terraform output instance_public_ip

# View sensitive output
terraform output -raw db_connection_string

# JSON format (for scripts)
terraform output -json
```

---

## Data Sources

Data sources let you fetch information from existing infrastructure — things not managed by your Terraform code.

```hcl
# Look up the latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}

# Use in a resource
resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
}

# Look up current AWS account info
data "aws_caller_identity" "current" {}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

# Look up existing VPC
data "aws_vpc" "existing" {
  filter {
    name   = "tag:Name"
    values = ["production-vpc"]
  }
}
```

---

## State Management

Terraform state tracks the mapping between your configuration and real-world resources.

### Local State (Default)

```bash
# State is stored locally in terraform.tfstate
# Fine for learning, NOT for teams
```

### Remote State (Production)

```hcl
# backend.tf — S3 + DynamoDB for state locking
terraform {
  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "devops-lab/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

### State Commands

```bash
# List all resources in state
terraform state list

# Show details of a resource
terraform state show aws_instance.web

# Move resource (rename without destroy/recreate)
terraform state mv aws_instance.old aws_instance.new

# Remove resource from state (keeps real resource)
terraform state rm aws_instance.web

# Import existing resource into state
terraform import aws_instance.web i-1234567890abcdef0

# Force unlock state (use with caution)
terraform force-unlock LOCK_ID
```

---

## Best Practices

### Code Organization

1. **Use consistent file naming:** `main.tf`, `variables.tf`, `outputs.tf`, `providers.tf`
2. **Use modules** for reusable components
3. **Use workspaces or directory structure** for environments (dev/staging/prod)
4. **Pin provider versions** to avoid breaking changes

### Security

1. **Never commit `.tfvars` files** with sensitive data (add to `.gitignore`)
2. **Use remote state** with encryption
3. **Enable state locking** to prevent concurrent modifications
4. **Mark sensitive outputs** with `sensitive = true`
5. **Use IAM roles** instead of hardcoded credentials

### Workflow

1. **Always run `terraform plan`** before `apply`
2. **Review plans carefully** — especially `destroy` operations
3. **Use `-target` sparingly** — it can lead to state drift
4. **Tag everything** for cost allocation and management
5. **Use `terraform fmt`** to maintain consistent formatting

---

## Project Structure

### Simple Project

```
project/
├── main.tf           # Primary resources
├── variables.tf      # Input variables
├── outputs.tf        # Output values
├── providers.tf      # Provider configuration
├── backend.tf        # State backend configuration
├── terraform.tfvars  # Variable values (gitignored if sensitive)
└── .gitignore
```

### Multi-Environment

```
terraform/
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── ec2/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   └── prod/
│       ├── main.tf
│       ├── terraform.tfvars
│       └── backend.tf
└── .gitignore
```

---

[← Back to Terraform](README.md)
