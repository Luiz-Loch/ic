# IAM Role
# ==============================
resource "aws_iam_role" "this" {
  name        = "${local.name}-ec2-role"
  description = "IAM Role for EC2 ${local.name}"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ec2.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}


# ==============================
resource "aws_iam_role_policy_attachment" "AmazonEC2ReadOnlyAccess" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "AmazonS3FullAccess" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "CloudWatchAgent" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy_attachment" "SSMManagedInstanceCore" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# IAM Instance Profile
# ==============================
resource "aws_iam_instance_profile" "this" {
  name = "${local.name}-ec2-profile"
  role = aws_iam_role.this.name
}

# AWS Key pair
# ==============================
resource "aws_key_pair" "this" {
  key_name = "${local.name}-aws-key"
  public_key = file("~/.ssh/tf-ic-key.pub")
}

# Security Group
# ==============================
resource "aws_security_group" "this" {
  name        = "${local.name}-ec2-sg"
  description = "Security group for EC2 ${local.name}"
  vpc_id      = aws_vpc.this.id

  ingress {
    description = "Allow SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { "Name" = "${local.name}-ec2-sg" }
}

# AWS EC2 instance
# ==============================
resource "aws_instance" "this" {
  ami = "ami-0e1bed4f06a3b463d" # Canonical, Ubuntu, 22.04, amd64 jammy image - us-east-1
  associate_public_ip_address = true
  instance_type               = "t3.xlarge" # $0.1664/hora
  # instance_type = "g5.xlarge" # $1.013/hora
  # instance_type = "g4dn.xlarge" # $0.525/hora
  vpc_security_group_ids = [aws_security_group.this.id]
  key_name                    = aws_key_pair.this.key_name
  iam_instance_profile        = aws_iam_instance_profile.this.name
  subnet_id                   = aws_subnet.public_subnet_1.id
  user_data = file("./setup.sh")

  root_block_device {
    volume_size           = 50
    volume_type           = "gp3"
    delete_on_termination = true
  }

  tags = {
    "Name" = "${local.name}-ec2-instance"
  }
}