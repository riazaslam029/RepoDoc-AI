import httpx
from typing import Optional
from app.config import settings


class GitHubClient:
    def __init__(self):
        self.base_url = settings.GITHUB_API_URL
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        if settings.GITHUB_TOKEN:
            self.headers['Authorization'] = f'token {settings.GITHUB_TOKEN}'

    async def _request(self, method: str, url: str, **kwargs) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()

    async def get_repository(self, owner: str, repo: str) -> dict:
        url = f'{self.base_url}/repos/{owner}/{repo}'
        return await self._request('GET', url)

    async def get_languages(self, owner: str, repo: str) -> dict:
        url = f'{self.base_url}/repos/{owner}/{repo}/languages'
        return await self._request('GET', url)

    async def get_readme(self, owner: str, repo: str) -> Optional[str]:
        url = f'{self.base_url}/repos/{owner}/{repo}/readme'
        try:
            result = await self._request('GET', url)
            import base64
            return base64.b64decode(result['content']).decode('utf-8')
        except httpx.HTTPStatusError:
            return None

    async def get_tree(self, owner: str, repo: str, branch: str = 'main') -> dict:
        url = f'{self.base_url}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1'
        return await self._request('GET', url)

    async def get_file_content(self, owner: str, repo: str, path: str, ref: str = 'main') -> Optional[str]:
        url = f'{self.base_url}/repos/{owner}/{repo}/contents/{path}?ref={ref}'
        try:
            result = await self._request('GET', url)
            if isinstance(result, list):
                return None
            import base64
            return base64.b64decode(result['content']).decode('utf-8')
        except httpx.HTTPStatusError:
            return None

    async def get_workflows(self, owner: str, repo: str) -> list:
        url = f'{self.base_url}/repos/{owner}/{repo}/actions/workflows'
        try:
            result = await self._request('GET', url)
            return result.get('workflows', [])
        except httpx.HTTPStatusError:
            return []

    async def get_license(self, owner: str, repo: str) -> Optional[dict]:
        url = f'{self.base_url}/repos/{owner}/{repo}/license'
        try:
            return await self._request('GET', url)
        except httpx.HTTPStatusError:
            return None

    async def get_contributing(self, owner: str, repo: str) -> Optional[str]:
        for filename in ['CONTRIBUTING.md', 'contributing.md', 'CONTRIBUTING.rst']:
            content = await self.get_file_content(owner, repo, filename)
            if content:
                return content
        return None