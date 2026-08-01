# AWS EC2 Deployment Configuration for RepoDoc AI Backend

## Prerequisites

1. AWS EC2 instance (t3.micro or larger) running Amazon Linux 2023
2. Security group allowing HTTP (port 80) and HTTPS (port 443)
3. EC2 IAM role with Bedrock permissions
4. SSH key pair for instance access
5. AWS CLI configured on your local machine

## Architecture

The backend runs on an EC2 instance with:
- **Python 3.12** virtual environment
- **Uvicorn** ASGI server (2 workers)
- **systemd** service manager for process management and auto-restart
- **Nginx** reverse proxy for port 80/443 traffic
- **Amazon Linux 2023** OS

## Deployment Steps

### 1. Launch EC2 Instance

1. Go to AWS EC2 Console
2. Launch Instance → Amazon Linux 2023 AMI
3. Instance type: t3.micro (minimum) or t3.small (recommended)
4. Configure security group: allow ports 80 (HTTP), 443 (HTTPS), 22 (SSH)
5. Create or select an existing IAM role with Bedrock permissions
6. Launch the instance

### 2. Connect to Instance

```bash
ssh -i your-key.pem ec2-user@<instance-public-ip>
```

### 3. Run Setup Script

Copy the user-data script and run it:

```bash
# On your local machine
scp -i your-key.pem deploy/ec2-user-data.sh ec2-user@<instance-ip>:~/

# SSH into the instance
ssh -i your-key.pem ec2-user@<instance-ip>

# Run the setup script
chmod +x ~/ec2-user-data.sh
sudo ~/ec2-user-data.sh
```

### 4. Verify Deployment

```bash
# Check service status
sudo systemctl status repodoc-ai

# Check logs
sudo journalctl -u repodoc-ai -f

# Test the health endpoint
curl http://localhost:8000/health
```

Expected response: `{"status":"ok","version":"1.0.0"}`

### 5. Verify After Reboot

```bash
# Reboot the instance
sudo reboot

# After reboot, check the service
sudo systemctl status repodoc-ai
curl http://localhost:8000/health
```

The systemd service is enabled to start automatically on boot.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_REGION` | Yes | `ap-south-1` | AWS region for Bedrock |
| `BEDROCK_MODEL_ID` | No | `anthropic.claude-3-haiku-20240307` | Amazon Bedrock model identifier |
| `GITHUB_TOKEN` | Yes | *(empty)* | GitHub personal access token for repo access |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-separated list of allowed CORS origins |
| `PORT` | No | `8000` | Port the server listens on (EC2) |

## IAM Role Permissions

The EC2 instance profile needs the following IAM permissions for Amazon Bedrock:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/*"
    }
  ]
}
```

boto3 automatically uses the EC2 IAM role for Bedrock access — no `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` environment variables are needed.

## Monitoring

```bash
# View service logs
sudo journalctl -u repodoc-ai -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check service status
sudo systemctl status repodoc-ai

# Restart service
sudo systemctl restart repodoc-ai
```

## Nginx Configuration

The setup script creates `/etc/nginx/conf.d/repodoc-ai.conf`:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Systemd Service

The service file is located at `/etc/systemd/system/repodoc-ai.service`:

- **User**: `ec2-user`
- **Working Directory**: `/home/ec2-user/repodoc-ai/backend`
- **Port**: 8000
- **Workers**: 2 (Uvicorn)
- **Restart**: on-failure (10s delay)
- **Log**: journald (`journalctl -u repodoc-ai`)