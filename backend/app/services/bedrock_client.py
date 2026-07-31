import json
import time
import logging
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from typing import Optional, AsyncGenerator
from app.config import settings

logger = logging.getLogger(__name__)


class BedrockError(Exception):
    def __init__(self, message: str, error_code: str = '', status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class ThrottlingError(BedrockError):
    def __init__(self, message: str = 'Bedrock throttling limit exceeded'):
        super().__init__(message, error_code='ThrottlingException', status_code=429)


class AccessDeniedError(BedrockError):
    def __init__(self, message: str = 'Bedrock access denied'):
        super().__init__(message, error_code='AccessDeniedException', status_code=403)


class ModelNotFoundError(BedrockError):
    def __init__(self, message: str = 'Bedrock model not found'):
        super().__init__(message, error_code='ModelNotFoundError', status_code=404)


class BedrockClient:
    _instance = None
    _failure_count = 0
    _last_failure_time = 0.0
    _circuit_open = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.model_id = settings.BEDROCK_MODEL_ID
        self.max_retries = settings.MAX_RETRIES
        self.retry_delay = settings.RETRY_DELAY
        self.circuit_threshold = 5
        self.circuit_reset_timeout = 60
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

    def _check_circuit(self) -> bool:
        if not self._circuit_open:
            return True
        if time.time() - self._last_failure_time > self.circuit_reset_timeout:
            self._circuit_open = False
            self._failure_count = 0
            logger.info('Circuit breaker reset')
            return True
        return False

    def _record_failure(self):
        self._failure_count += 1
        self._last_failure_time = time.time()
        if self._failure_count >= self.circuit_threshold:
            self._circuit_open = True
            logger.warning('Circuit breaker opened after %d failures', self._failure_count)

    def _record_success(self):
        self._failure_count = 0
        self._circuit_open = False

    async def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.3) -> str:
        if not self._check_circuit():
            raise BedrockError('Bedrock service is temporarily unavailable (circuit open)')

        last_exception = None
        for attempt in range(self.max_retries):
            try:
                result = await self._invoke(prompt, max_tokens, temperature)
                self._record_success()
                return result
            except ThrottlingError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (attempt + 1) * 2
                    logger.warning('Throttled, retrying in %.1fs (attempt %d/%d)', delay, attempt + 1, self.max_retries)
                    import asyncio
                    await asyncio.sleep(delay)
                    continue
            except AccessDeniedError as e:
                self._record_failure()
                raise
            except ModelNotFoundError as e:
                self._record_failure()
                raise
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                if error_code == 'ThrottlingException':
                    last_exception = ThrottlingError(str(e))
                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay * (attempt + 1) * 2
                        logger.warning('Throttled, retrying in %.1fs (attempt %d/%d)', delay, attempt + 1, self.max_retries)
                        import asyncio
                        await asyncio.sleep(delay)
                        continue
                elif error_code == 'AccessDeniedException':
                    raise AccessDeniedError(str(e))
                elif error_code == 'ModelNotFound':
                    raise ModelNotFoundError(str(e))
                last_exception = BedrockError(str(e), error_code=error_code)
            except Exception as e:
                last_exception = BedrockError(str(e))

        self._record_failure()
        raise last_exception or BedrockError('Bedrock generation failed')

    async def generate_stream(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.3) -> AsyncGenerator[str, None]:
        if not self._check_circuit():
            raise BedrockError('Bedrock service is temporarily unavailable (circuit open)')

        for attempt in range(self.max_retries):
            try:
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

                response = self.client.invoke_model_with_response_stream(
                    modelId=self.model_id,
                    body=body,
                    accept='application/json',
                    contentType='application/json',
                )

                for event in response['body']:
                    chunk = event.get('chunk', {})
                    if chunk.get('bytes'):
                        chunk_data = json.loads(chunk['bytes'].read())
                        if 'content' in chunk_data:
                            for content_block in chunk_data['content']:
                                if content_block.get('type') == 'text':
                                    yield content_block['text']

                self._record_success()
                return
            except ThrottlingError as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (attempt + 1) * 2
                    import asyncio
                    await asyncio.sleep(delay)
                    continue
                raise
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                if error_code == 'ThrottlingException':
                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay * (attempt + 1) * 2
                        import asyncio
                        await asyncio.sleep(delay)
                        continue
                    raise ThrottlingError(str(e))
                raise BedrockError(str(e), error_code=error_code)

        raise BedrockError('Bedrock streaming failed after max retries')

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

        if 'content' not in response_body or not response_body['content']:
            raise BedrockError('Empty response from Bedrock')

        return response_body['content'][0]['text']

    async def health_check(self) -> dict:
        try:
            response = self.client.list_foundation_models()
            models = response.get('modelSummaries', [])
            model_ids = [m['modelId'] for m in models]
            model_available = self.model_id in model_ids
            return {
                'status': 'healthy' if model_available else 'degraded',
                'model_id': self.model_id,
                'model_available': model_available,
                'available_models': len(models),
            }
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            return {
                'status': 'unhealthy',
                'error': error_code,
                'message': str(e),
            }

    def get_model_info(self) -> dict:
        return {
            'model_id': self.model_id,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'circuit_open': self._circuit_open,
            'failure_count': self._failure_count,
        }