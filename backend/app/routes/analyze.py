from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
from app.services.analyzer import analyze_repository
from app.services.bedrock_client import generate_documentation

router = APIRouter()


class AnalyzeRequest(BaseModel):
    repo_url: str


class AnalyzeResponse(BaseModel):
    repository: dict
    tech_stack: dict
    folder_structure: str
    architecture_summary: str
    readme_content: str
    installation_guide: str
    api_documentation: str
    health_score: dict
    suggestions: list[str]


@router.post('/analyze', response_model=AnalyzeResponse)
async def analyze_repo(request: AnalyzeRequest):
    try:
        repo_data = await analyze_repository(request.repo_url)
        readme_content = await generate_documentation(repo_data, 'readme')
        installation_guide = await generate_documentation(repo_data, 'installation')
        architecture_summary = await generate_documentation(repo_data, 'architecture')
        api_documentation = await generate_documentation(repo_data, 'api')
        health_score = await generate_documentation(repo_data, 'health_score')
        suggestions = await generate_documentation(repo_data, 'suggestions')

        return AnalyzeResponse(
            repository=repo_data.get('repository', {}),
            tech_stack=repo_data.get('tech_stack', {}),
            folder_structure=repo_data.get('folder_structure', ''),
            architecture_summary=architecture_summary,
            readme_content=readme_content,
            installation_guide=installation_guide,
            api_documentation=api_documentation,
            health_score=health_score,
            suggestions=suggestions,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))