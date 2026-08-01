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
| AWS         | Amplify, App Runner   |
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
- **Backend**: AWS App Runner (FastAPI container)
- **AI**: Amazon Bedrock (Nova Lite)

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

### Docker Build

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
  --instance-configuration CPU=1,Memory=2GB \
  --environment-variables Variable=[{Name=AWS_REGION,Value=ap-south-1},{Name=BEDROCK_MODEL_ID,Value=anthropic.claude-3-haiku-20240307},{Name=CORS_ORIGINS,Value=https://repodoc-ai.netlify.app}]
```

3. App Runner automatically provides a service URL (e.g., `https://<service-id>.apprunner.amazonaws.com`).

4. Connect the Amplify frontend by setting the `VITE_API_URL` environment variable in Amplify to the App Runner service URL.

### Environment Variables

All environment variables are read from the `.env` file or set directly in the App Runner configuration. Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_REGION` | Yes | `ap-south-1` | AWS region for Bedrock |
| `BEDROCK_MODEL_ID` | No | `anthropic.claude-3-haiku-20240307` | Amazon Bedrock model identifier |
| `GITHUB_TOKEN` | Yes | *(empty)* | GitHub personal access token for repo access |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-separated list of allowed CORS origins |
| `PORT` | No | `8080` | Port the server listens on (App Runner) |

### IAM Role Permissions

The App Runner service role needs the following IAM permissions for Amazon Bedrock:

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

boto3 automatically uses the App Runner IAM role for Bedrock access — no `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` environment variables are needed.

## License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.