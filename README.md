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

- **Frontend**: AWS Amplify
- **Backend**: AWS Lambda + API Gateway (or App Runner)
- **AI**: Amazon Bedrock (Nova Lite)

## License

MIT

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.