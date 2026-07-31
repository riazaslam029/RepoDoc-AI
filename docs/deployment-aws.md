# AWS Lambda Deployment Configuration for RepoDoc AI Backend

## Prerequisites

1. AWS Account with Lambda, API Gateway, and IAM access
2. AWS CLI configured
3. Docker installed (for containerized deployment)

## Option 1: AWS Lambda with Container Image

### 1. Create Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Build and Push to ECR

```bash
aws ecr create-repository --repository-name repodoc-ai-backend
docker build -t repodoc-ai-backend .
docker tag repodoc-ai-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/repodoc-ai-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/repodoc-ai-backend:latest
```

### 3. Create Lambda Function

```bash
aws lambda create-function \
  --function-name repodoc-ai-backend \
  --package-type Image \
  --code ImageUri=<account-id>.dkr.ecr.<region>.amazonaws.com/repodoc-ai-backend:latest \
  --role <iam-role-arn> \
  --timeout 30 \
  --memory-size 512
```

### 4. Create API Gateway

```bash
aws apigateway create-rest-api --name 'RepoDoc AI API'
```

## Option 2: AWS App Runner

### 1. Create App Runner Service

```bash
aws apprunner create-service \
  --service-name repodoc-ai-backend \
  --source-configuration '
    {
      "AuthenticationConfiguration": {
        "AccessRoleArn": "<iam-role-arn>"
      },
      "AutoConfigurationsEnabled": true,
      "ImageRepository": {
        "ImageIdentifier": "<account-id>.dkr.ecr.<region>.amazonaws.com/repodoc-ai-backend:latest",
        "ImageRepositoryType": "ECR",
        "ImageConfiguration": {
          "Port": 8000
        }
      }
    }
  ' \
  --instance-configuration '
    {
      "Cpu": 1,
      "Memory": 2,
      "InstanceRoleArn": "<iam-role-arn>"
    }
  '
```

## Environment Variables

Set the following environment variables for the Lambda/App Runner:

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_REGION` | AWS region | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key | Your key |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Your secret |
| `BEDROCK_MODEL_ID` | Bedrock model ID | `anthropic.claude-3-haiku-20240307` |
| `GITHUB_TOKEN` | GitHub personal access token | Your token |
| `CORS_ORIGINS` | Allowed CORS origins | `https://repodoc.ai` |

## IAM Permissions

The Lambda/App Runner needs the following IAM permissions:

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
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-20240307"
    }
  ]
}
```

## Monitoring

- Use AWS CloudWatch for logs
- Set up alarms for error rates and latency
- Monitor Lambda/App Runner metrics in AWS Console