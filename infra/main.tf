resource "aws_s3_bucket" "data" {
  bucket = "secure-by-design-demo-data"
}

# Public bucket: all four blocks disabled.
resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# SSH open to the whole internet.
resource "aws_security_group" "ssh" {
  name = "allow-ssh"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
