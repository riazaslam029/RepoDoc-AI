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
| AWS         | Amplify, Lambda, API Gateway, S3    |
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
- **Backend**: AWS App Runner (FastAPI container) or AWS Lambda (FastAPI container image)
- **AI**: Amazon Bedrock (Nova Lite)
- **API**: Amazon App Runner URL or API Gateway (REST API)

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

### Docker Build (App Runner)

Build the Docker image for App Runner deployment:

```bash
docker build -t repodoc-ai-backend .
```

### App Runner Deployment

1. Push the Docker image to Amazon ECR:

```bash
aws ecr create-repository --repository-name repodoc-ai-backend
docker tag repodoc-ai-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/repodoc-ai-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/repodoc-ai-backend:latest
```

2. Create an App Runner service:

```bash
aws apprunner create-service \
  --service-name repodoc-ai-backend \
  --source-configuration ImageRepository="{ImageRepositoryType=ECR,ImageIdentifier=<account-id>.dkr.ecr.<region>.amazonaws.com/repodoc-ai-backend:latest}" \
  --instance-configuration InstanceSize=SMALL \
  --environment-variables Variable=[{Name=AWS_REGION,Value=us-east-1},{Name=GITHUB_TOKEN,Value=<github-token>},{Name=CORS_ORIGINS,Value=https://repodoc.ai}]
```

3. App Runner automatically provides a service URL (e.g., `https://<service-id>.apprunner.amazonaws.com`).

### Lambda Deployment

1. Build and push the Docker image to Amazon ECR:

```bash
aws ecr create-repository --repository-name repodoc-ai-backend
docker tag repodoc-ai-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/repodoc-ai-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/repodoc-ai-backend:latest
```

2. Create the Lambda function:

```bash
aws lambda create-function \
  --function-name repodoc-ai-backend \
  --package-type Image \
  --code ImageUri=<account-id>.dkr.ecr.<region>.amazonaws.com/repodoc-ai-backend:latest \
  --role <iam-role-arn> \
  --timeout 30 \
  --memory-size 512
```

3. Set environment variables in the Lambda configuration:

| Variable | Description |
|----------|-------------|
| `AWS_REGION` | AWS region (e.g., `us-east-1`) |
| `AWS_ACCESS_KEY_ID` | AWS access key for Bedrock |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key for Bedrock |
| `BEDROCK_MODEL_ID` | Bedrock model ID |
| `GITHUB_TOKEN` | GitHub personal access token |
| `CORS_ORIGINS` | Comma-separated list of allowed origins (e.g., `https://repodoc.ai`) |

4. Create API Gateway and integrate with the Lambda function.

### Environment Variables

All environment variables are read from the `.env` file or set directly in the deployment environment. Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_REGION` | Yes | `us-east-1` | AWS region for Bedrock and other services |
| `AWS_ACCESS_KEY_ID` | Yes | *(empty)* | AWS access key ID for Bedrock access |
| `AWS_SECRET_ACCESS_KEY` | Yes | *(empty)* | AWS secret access key for Bedrock access |
| `BEDROCK_MODEL_ID` | No | `anthropic.claude-3-haiku-20240307` | Amazon Bedrock model identifier |
| `GITHUB_TOKEN` | Yes | *(empty)* | GitHub personal access token for repo access |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-separated list of allowed CORS origins |
| `PORT` | No | `8080` | Port the server listens on (App Runner) |

### Environment Variables for Bedrock IAM Permissions

The Lambda/App Runner service role needs the following IAM permissions for Amazon Bedrock:

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

MIT

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.