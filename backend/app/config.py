import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    AWS_REGION: str = os.getenv('AWS_REGION', 'ap-south-1')
    BEDROCK_MODEL_ID: str = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307')
    GITHUB_TOKEN: str = os.getenv('GITHUB_TOKEN', '')
    GITHUB_API_URL: str = 'https://api.github.com'
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    CORS_ORIGINS: list[str] = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')


settings = Settings()