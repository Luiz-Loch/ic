# VPC
# ==============================
resource "aws_vpc" "this" {
  cidr_block = "10.1.0.0/16" # 65,536 IPs availables
  tags = { "Name" : "${local.name}-vpc" }
}

# Public subnets
# ==============================
resource "aws_subnet" "public_subnet_1" {
  vpc_id            = aws_vpc.this.id
  cidr_block = "10.1.0.0/24" # 256 IPs available
  availability_zone = "${local.region}a"
  map_public_ip_on_launch = true
  tags = { "Name" : "${local.name}-subnet-1-public" }
}

# resource "aws_subnet" "public_subnet_2" {
#   vpc_id            = aws_vpc.this.id
#   cidr_block = "10.1.1.0/24" # 256 IPs available
#   availability_zone = "${local.region}b"
#   tags = { "Name" : "${local.name}-subnet-2-public" }
# }

# Internet Gateway
# ==============================
resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
  tags = {"Name": "${local.name}-internet-gateway"}
}

# Route table
# ==============================
resource "aws_route_table" "this" {
  vpc_id = aws_vpc.this.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }
  tags = {"Name": "${local.name}-route-table-public"}
}

resource "aws_route_table_association" "public_subnet_1" {
  subnet_id      = aws_subnet.public_subnet_1.id
  route_table_id = aws_route_table.this.id
}