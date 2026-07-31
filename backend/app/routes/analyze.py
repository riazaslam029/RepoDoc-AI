from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
from app.services.analyzer import RepositoryAnalyzer
from app.services.bedrock_client import BedrockClient
from app.services.prompt_engine import generate_documentation
from app.services.health_score import HealthScorer

router = APIRouter()

bedrock = BedrockClient()


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


class ValidateRequest(BaseModel):
    repo_url: str


class ValidateResponse(BaseModel):
    valid: bool
    error: Optional[str] = None
    owner: Optional[str] = None
    repo: Optional[str] = None


@router.get('/health')
async def health_check():
    return {'status': 'ok', 'version': '1.0.0'}


@router.get('/health/bedrock')
async def bedrock_health_check():
    try:
        result = await bedrock.health_check()
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post('/validate', response_model=ValidateResponse)
async def validate_repo(request: ValidateRequest):
    try:
        owner, repo = RepositoryAnalyzer()._parse_url(request.repo_url)
        return ValidateResponse(valid=True, owner=owner, repo=repo)
    except ValueError as e:
        return ValidateResponse(valid=False, error=str(e))


@router.post('/analyze', response_model=AnalyzeResponse)
async def analyze_repo(request: AnalyzeRequest):
    try:
        analyzer = RepositoryAnalyzer()
        owner, repo = analyzer._parse_url(request.repo_url)

        repo_data = await analyzer.github.get_repository(owner, repo)
        if repo_data.get('private'):
            raise HTTPException(status_code=400, detail='Private repositories are not supported')
        if repo_data.get('archived'):
            raise HTTPException(status_code=400, detail='Archived repositories are not supported')

        analysis = await analyzer.analyze(request.repo_url)

        try:
            readme_content = await generate_documentation(analysis, 'readme')
        except Exception as e:
            readme_content = f'# {analysis["repository"]["name"]}\n\n{analysis["repository"]["description"] or "No description"}'

        try:
            installation_guide = await generate_documentation(analysis, 'installation')
        except Exception:
            installation_guide = ''

        try:
            architecture_summary = await generate_documentation(analysis, 'architecture')
        except Exception:
            architecture_summary = ''

        try:
            api_documentation = await generate_documentation(analysis, 'api')
        except Exception:
            api_documentation = ''

        try:
            health_scorer = HealthScorer(analysis)
            health_score_data = health_scorer.compute_overall()
            suggestions_data = health_scorer.get_suggestions()
        except Exception:
            health_score_data = {'overall': 0}
            suggestions_data = []

        try:
            suggestions = await generate_documentation(analysis, 'suggestions')
        except Exception:
            suggestions = suggestions_data

        return AnalyzeResponse(
            repository=analysis.get('repository', {}),
            tech_stack=analysis.get('tech_stack', {}),
            folder_structure=analysis.get('folder_structure', ''),
            architecture_summary=architecture_summary,
            readme_content=readme_content,
            installation_guide=installation_guide,
            api_documentation=api_documentation,
            health_score=health_score_data,
            suggestions=suggestions if isinstance(suggestions, list) else [suggestions] if suggestions else suggestions_data,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))