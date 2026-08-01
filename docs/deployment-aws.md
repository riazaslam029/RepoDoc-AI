# AWS App Runner Deployment Configuration for RepoDoc AI Backend

## Prerequisites

1. AWS Account with App Runner, ECR, and IAM access
2. AWS CLI configured
3. Docker installed (for building the container image)

## Architecture

The backend is deployed as a container image on AWS App Runner, which provides:
- Automatic scaling
- Managed infrastructure
- Built-in load balancing
- SSL/TLS termination

## Deployment Steps

### 1. Create ECR Repository

```bash
aws ecr create-repository --repository-name repodoc-ai-backend
```

### 2. Build and Push Docker Image

```bash
docker build -t repodoc-ai-backend .
docker tag repodoc-ai-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/repodoc-ai-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/repodoc-ai-backend:latest
```

### 3. Create App Runner Service

```bash
aws apprunner create-service \
  --service-name repodoc-ai-backend \
  --source-configuration ImageRepository="{ImageRepositoryType=ECR,ImageIdentifier=<account-id>.dkr.ecr.<region>.amazonaws.com/repodoc-ai-backend:latest}" \
  --instance-configuration CPU=1,Memory=2GB \
  --environment-variables Variable=[{Name=AWS_REGION,Value=ap-south-1},{Name=BEDROCK_MODEL_ID,Value=anthropic.claude-3-haiku-20240307},{Name=CORS_ORIGINS,Value=https://repodoc-ai.netlify.app}]
```

### 4. Get the Service URL

App Runner automatically provides a service URL (e.g., `https://<service-id>.apprunner.amazonaws.com`).

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_REGION` | Yes | `ap-south-1` | AWS region for Bedrock |
| `BEDROCK_MODEL_ID` | No | `anthropic.claude-3-haiku-20240307` | Amazon Bedrock model identifier |
| `GITHUB_TOKEN` | Yes | *(empty)* | GitHub personal access token for repo access |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-separated list of allowed CORS origins |
| `PORT` | No | `8080` | Port the server listens on (App Runner) |

## IAM Permissions

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

## Monitoring

- Use AWS CloudWatch for logs
- Set up alarms for error rates and latency
- Monitor App Runner metrics in AWS Console