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
- **Backend**: AWS Lambda (FastAPI container image)
- **AI**: Amazon Bedrock (Nova Lite)
- **API**: Amazon API Gateway (REST API)

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

Build the Docker image for Lambda container deployment:

```bash
docker build -t repodoc-ai-backend .
```

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

### API Gateway Deployment

1. Create a REST API in API Gateway:

```bash
aws apigateway create-rest-api --name 'RepoDoc AI API'
```

2. Create a resource and method that integrates with the Lambda function:

```bash
aws apigateway put-method \
  --rest-api-id <api-id> \
  --resource-id <resource-id> \
  --http-method ANY \
  --authorization-type NONE

aws apigateway put-integration \
  --rest-api-id <api-id> \
  --resource-id <resource-id> \
  --http-method ANY \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:<region>:lambda:path/2015-03-31/functions/arn:aws:lambda:<region>:<account-id>:function:repodoc-ai-backend/invocations
```

3. Deploy the API:

```bash
aws apigateway create-deployment \
  --rest-api-id <api-id> \
  --stage-name prod
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

## License

MIT

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.