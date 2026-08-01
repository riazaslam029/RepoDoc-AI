# AWS Amplify Deployment Configuration for RepoDoc AI Frontend

## Prerequisites

1. AWS Account with Amplify access
2. GitHub repository connected to AWS Amplify
3. Environment variables configured in Amplify Console

## Setup Steps

### 1. Connect Repository

1. Go to AWS Amplify Console
2. Click "New app" > "Host web app"
3. Connect your GitHub repository: `riazaslam029/RepoDoc-AI`
4. Select the `main` branch

### 2. Configure Build Settings

Amplify will auto-detect the Vite build configuration. The build settings should be:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/dist
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

### 3. Environment Variables

### 4. Custom Domain (Optional)

1. Go to Amplify Console > App settings > Domain management
2. Add your custom domain
3. Follow the DNS configuration instructions

### 5. Deploy

1. Push to `main` branch
2. Amplify will automatically build and deploy
3. Monitor the build in the Amplify Console

## CI/CD

Amplify automatically builds and deploys on every push to `main` and on pull requests.

## Monitoring

- Use AWS CloudWatch for logs
- Set up alarms for error rates
- Monitor build durations