# RepoDoc AI

AI-powered GitHub Documentation Assistant that automatically analyzes GitHub repositories and generates professional documentation using Amazon Bedrock.

## Tagline

Automate your project documentation with AI. Paste a GitHub URL and get a complete, professional README.

## Features

- **Repository Analysis** — Fetches and analyzes any public GitHub repository
- **README Generation** — AI-generated professional README.md using Amazon Bedrock
- **Tech Stack Detection** — Automatically detects languages, frameworks, and dependencies
- **Architecture Summary** — Generates an architecture overview from code structure
- **API Documentation** — Extracts and documents API endpoints when applicable
- **Documentation Health Score** — Scores your documentation quality out of 100
- **Markdown Export** — Download generated documentation as Markdown
- **Improvement Suggestions** — AI-powered tips to improve your docs

## Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Frontend    | React, Vite, Tailwind CSS, TypeScript |
| Backend     | FastAPI, Python                     |
| AI          | Amazon Bedrock, Nova Lite           |
| AWS         | Amplify, EC2, Nginx   |
| GitHub      | GitHub REST API                     |

## Project Structure

```
frontend/          # React application (Vite + Tailwind + TypeScript)
backend/           # FastAPI application (Python)
docs/              # Documentation and architecture diagrams
prompts/           # Prompt templates for Bedrock
tests/             # Shared and integration tests
.github/           # GitHub Actions workflows
```

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- AWS account with Bedrock access
- GitHub personal access token

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

## AWS Deployment

### Architecture

- **Frontend**: AWS Amplify (React SPA)
- **Backend**: AWS EC2 (Amazon Linux 2023, systemd + Uvicorn)
- **AI**: Amazon Bedrock (Nova Lite)
- **Web Server**: Nginx (reverse proxy)

### Local Development

#### Prerequisites

- Node.js 18+
- Python 3.11+
- AWS account with Bedrock access
- GitHub personal access token

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### EC2 Deployment (Amazon Linux 2023)

#### Prerequisites

- AWS EC2 instance (t3.micro or larger) running Amazon Linux 2023
- Security group allowing HTTP (port 80) and HTTPS (port 443)
- EC2 IAM role with Bedrock permissions
- SSH key pair for instance access

#### Step 1: Launch EC2 Instance

1. Launch an EC2 instance with Amazon Linux 2023 AMI
2. Instance type: t3.micro (minimum) or t3.small (recommended)
3. Attach an IAM role with Bedrock permissions (see below)
4. Configure security group to allow ports 80 and 443

#### Step 2: Connect to Instance

```bash
ssh -i your-key.pem ec2-user@<instance-public-ip>
```

#### Step 3: Run Setup Script

Copy the user-data script to the instance and run it, or use EC2 user-data:

```bash
# On your local machine, copy the setup script
scp -i your-key.pem deploy/ec2-user-data.sh ec2-user@<instance-ip>:~/

# SSH into the instance
ssh -i your-key.pem ec2-user@<instance-ip>

# Run the setup script
chmod +x ~/ec2-user-data.sh
sudo ~/ec2-user-data.sh
```

#### Step 4: Verify Deployment

```bash
# Check service status
sudo systemctl status repodoc-ai

# Check logs
sudo journalctl -u repodoc-ai -f

# Test the health endpoint
curl http://localhost:8000/health
```

#### Step 5: Connect Amplify Frontend

The setup script builds the frontend and deploys it via Nginx. Set the `VITE_API_URL` environment variable in Amplify to the EC2 instance URL (though with the new same-origin architecture, this is no longer required — Nginx handles routing):

```
# Optional: Only needed if using a custom domain or separate backend URL
VITE_API_URL=http://<instance-public-ip>
```

Then rebuild and redeploy the Amplify frontend.

#### Step 6: Verify After Reboot

The systemd service is enabled to start on boot. Test:

```bash
# Reboot the instance
sudo reboot

# After reboot, check the service
sudo systemctl status repodoc-ai
curl http://localhost:8000/health
```

### EC2 IAM Role Permissions

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

### Environment Variables

All environment variables are read from the `.env` file or set in the systemd service. Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_REGION` | Yes | `ap-south-1` | AWS region for Bedrock |
| `BEDROCK_MODEL_ID` | No | `anthropic.claude-3-haiku-20240307` | Amazon Bedrock model identifier |
| `GITHUB_TOKEN` | Yes | *(empty)* | GitHub personal access token for repo access |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-separated list of allowed CORS origins (for dev only; not needed in production) |
| `PORT` | No | `8000` | Port the server listens on (EC2) |

### Systemd Service

The backend runs as a systemd service (`repodoc-ai.service`) with the following configuration:

- **User**: `ec2-user`
- **Working Directory**: `/home/ec2-user/repodoc-ai/backend`
- **Port**: 8000
- **Workers**: 2 (Uvicorn)
- **Restart**: on-failure (10s delay)
- **Log**: journald (`journalctl -u repodoc-ai`)

### Monitoring

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

## License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.