import json
import os
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from typing import Optional
from app.config import settings


class BedrockClient:
    def __init__(self):
        self.model_id = settings.BEDROCK_MODEL_ID
        self.max_retries = settings.MAX_RETRIES
        self.retry_delay = settings.RETRY_DELAY
        self.client = self._create_client()

    def _create_client(self):
        config = Config(
            retries={'max_attempts': 3, 'mode': 'adaptive'},
            connect_timeout=10,
            read_timeout=60,
        )
        return boto3.client(
            'bedrock-runtime',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
            config=config,
        )

    async def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.3) -> str:
        for attempt in range(self.max_retries):
            try:
                return await self._invoke(prompt, max_tokens, temperature)
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                if error_code == 'ThrottlingException' and attempt < self.max_retries - 1:
                    import asyncio
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                if error_code == 'AccessDeniedException':
                    raise RuntimeError(f'Bedrock access denied: {e}')
                raise RuntimeError(f'Bedrock invocation failed: {e}')
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f'Bedrock generation failed after {self.max_retries} attempts: {e}')
                import asyncio
                await asyncio.sleep(self.retry_delay * (attempt + 1))

        raise RuntimeError('Max retries exceeded')

    async def _invoke(self, prompt: str, max_tokens: int, temperature: float) -> str:
        body = json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': max_tokens,
            'temperature': temperature,
            'messages': [
                {
                    'role': 'user',
                    'content': [{'type': 'text', 'text': prompt}],
                }
            ],
        })

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body,
            accept='application/json',
            contentType='application/json',
        )

        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']