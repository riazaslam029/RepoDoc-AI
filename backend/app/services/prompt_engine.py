import asyncio
from typing import Optional
from app.services.bedrock_client import BedrockClient
from app.services.analyzer import RepositoryAnalyzer
from app.config import settings


bedrock = BedrockClient()
analyzer = RepositoryAnalyzer()


async def generate_documentation(repo_data: dict, doc_type: str) -> str:
    prompt = _build_prompt(doc_type, repo_data)
    if not prompt:
        return ''
    return await bedrock.generate(prompt)


def _build_prompt(doc_type: str, repo_data: dict) -> str:
    repo = repo_data.get('repository', {})
    tech = repo_data.get('tech_stack', {})

    templates = {
        'readme': _readme_prompt,
        'installation': _installation_prompt,
        'architecture': _architecture_prompt,
        'api': _api_prompt,
        'health_score': _health_score_prompt,
        'suggestions': _suggestions_prompt,
    }

    builder = templates.get(doc_type)
    if builder:
        return builder(repo, tech, repo_data)
    return ''


def _readme_prompt(repo: dict, tech: dict, data: dict) -> str:
    return README_PROMPT.format(
        repo_name=repo.get('name', 'Unknown'),
        description=repo.get('description') or 'No description',
        language=tech.get('language', 'Unknown'),
        topics=', '.join(repo.get('topics', [])),
        stars=repo.get('stargazers_count', 0),
        license=repo.get('license') or 'None',
        tech_stack='\n'.join(f'- {k}: {v}' for k, v in tech.items() if v and v != 'Not detected'),
        folder_structure=data.get('folder_structure', 'N/A'),
        dependencies=', '.join(tech.get('dependencies', [])),
        ci_cd=', '.join(tech.get('ci_cd', [])),
    )


def _installation_prompt(repo: dict, tech: dict, data: dict) -> str:
    return INSTALLATION_PROMPT.format(
        repo_name=repo.get('name', 'Unknown'),
        tech_stack=', '.join(v for v in tech.values() if v and v != 'Not detected'),
        dependencies=', '.join(tech.get('dependencies', [])),
        folder_structure=data.get('folder_structure', 'N/A'),
    )


def _architecture_prompt(repo: dict, tech: dict, data: dict) -> str:
    return ARCHITECTURE_PROMPT.format(
        repo_name=repo.get('name', 'Unknown'),
        language=tech.get('language', 'Unknown'),
        framework=tech.get('framework', 'Unknown'),
        database=tech.get('database', 'Unknown'),
        deployment=tech.get('deployment', 'Unknown'),
        folder_structure=data.get('folder_structure', 'N/A'),
    )


def _api_prompt(repo: dict, tech: dict, data: dict) -> str:
    return API_DOC_PROMPT.format(
        repo_name=repo.get('name', 'Unknown'),
        language=tech.get('language', 'Unknown'),
        framework=tech.get('framework', 'Unknown'),
        folder_structure=data.get('folder_structure', 'N/A'),
    )


def _health_score_prompt(repo: dict, tech: dict, data: dict) -> str:
    readme = data.get('readme', '')
    has_readme = bool(readme)
    readme_sections = _detect_readme_sections(readme) if has_readme else 'None'

    return HEALTH_SCORE_PROMPT.format(
        repo_name=repo.get('name', 'Unknown'),
        has_readme='Yes' if has_readme else 'No',
        has_license='Yes' if data.get('license_info') else 'No',
        has_contributing='Yes' if data.get('contributing') else 'No',
        readme_sections=readme_sections,
        has_examples='No',
        has_api_docs='No',
        has_architecture='No',
        has_screenshots='No',
    )


def _suggestions_prompt(repo: dict, tech: dict, data: dict) -> str:
    return SUGGESTIONS_PROMPT.format(
        repo_name=repo.get('name', 'Unknown'),
        tech_stack=', '.join(v for v in tech.values() if v and v != 'Not detected'),
        readme_quality='N/A',
        health_score='N/A',
        missing_elements='README, License, Contributing Guide',
    )


def _detect_readme_sections(readme: str) -> str:
    sections = []
    for line in readme.split('\n'):
        if line.startswith('#'):
            sections.append(line.strip('#').strip())
    return ', '.join(sections) if sections else 'None'