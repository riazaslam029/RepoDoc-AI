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
    readme_analysis = data.get('readme_analysis', {})
    dockerfile = data.get('dockerfile_analysis', {})
    actions = data.get('actions_analysis', {})

    tech_stack_lines = []
    for k, v in tech.items():
        if v and v != 'Not detected':
            if isinstance(v, list):
                tech_stack_lines.append(f'- {k}: {", ".join(v)}')
            else:
                tech_stack_lines.append(f'- {k}: {v}')

    return README_PROMPT.format(
        repo_name=repo.get('name', 'Unknown'),
        description=repo.get('description') or 'No description',
        language=tech.get('language', 'Unknown'),
        topics=', '.join(repo.get('topics', [])),
        stars=repo.get('stargazers_count', 0),
        license=repo.get('license') or 'None',
        tech_stack='\n'.join(tech_stack_lines),
        folder_structure=data.get('folder_structure', 'N/A'),
        dependencies=', '.join(data.get('dependencies', {}).get('all', [])),
        ci_cd=', '.join(tech.get('ci_cd', [])),
        has_badges='Yes' if readme_analysis.get('has_badges') else 'No',
        has_installation='Yes' if readme_analysis.get('has_installation') else 'No',
        has_usage='Yes' if readme_analysis.get('has_usage') else 'No',
        has_contributing='Yes' if readme_analysis.get('has_contributing') else 'No',
        has_api_reference='Yes' if readme_analysis.get('has_api_reference') else 'No',
        has_screenshots='Yes' if readme_analysis.get('has_screenshots') else 'No',
        readme_quality=readme_analysis.get('quality_score', 0),
        has_dockerfile='Yes' if dockerfile.get('base_image') else 'No',
        docker_base_image=dockerfile.get('base_image') or 'N/A',
        has_ci='Yes' if actions.get('ci_type') and actions['ci_type'] != 'Unknown' else 'No',
        ci_type=actions.get('ci_type', 'Unknown'),
        test_framework=actions.get('test_framework', 'Not detected'),
    )


def _installation_prompt(repo: dict, tech: dict, data: dict) -> str:
    dockerfile = data.get('dockerfile_analysis', {})
    deps = data.get('dependencies', {}).get('by_file', {})

    return INSTALLATION_PROMPT.format(
        repo_name=repo.get('name', 'Unknown'),
        tech_stack=', '.join(v for v in tech.values() if v and v != 'Not detected'),
        dependencies=', '.join(data.get('dependencies', {}).get('all', [])),
        folder_structure=data.get('folder_structure', 'N/A'),
        has_dockerfile='Yes' if dockerfile.get('base_image') else 'No',
        docker_base_image=dockerfile.get('base_image') or 'N/A',
        python_deps=', '.join(deps.get('requirements.txt', [])),
        node_deps=', '.join(deps.get('package.json', {}).get('dependencies', []) if isinstance(deps.get('package.json'), dict) else []),
    )


def _architecture_prompt(repo: dict, tech: dict, data: dict) -> str:
    dockerfile = data.get('dockerfile_analysis', {})
    actions = data.get('actions_analysis', {})

    return ARCHITECTURE_PROMPT.format(
        repo_name=repo.get('name', 'Unknown'),
        language=tech.get('language', 'Unknown'),
        framework=tech.get('framework', 'Unknown'),
        database=tech.get('database', 'Unknown'),
        deployment=tech.get('deployment', 'Unknown'),
        folder_structure=data.get('folder_structure', 'N/A'),
        has_dockerfile='Yes' if dockerfile.get('base_image') else 'No',
        docker_base_image=dockerfile.get('base_image') or 'N/A',
        docker_ports=dockerfile.get('exposed_ports', []),
        has_ci='Yes' if actions.get('ci_type') and actions['ci_type'] != 'Unknown' else 'No',
        ci_type=actions.get('ci_type', 'Unknown'),
        test_framework=actions.get('test_framework', 'Not detected'),
        has_deployment=actions.get('has_deployment_step', False),
    )


def _api_prompt(repo: dict, tech: dict, data: dict) -> str:
    readme_analysis = data.get('readme_analysis', {})

    return API_DOC_PROMPT.format(
        repo_name=repo.get('name', 'Unknown'),
        language=tech.get('language', 'Unknown'),
        framework=tech.get('framework', 'Unknown'),
        folder_structure=data.get('folder_structure', 'N/A'),
        has_api_reference='Yes' if readme_analysis.get('has_api_reference') else 'No',
        has_usage='Yes' if readme_analysis.get('has_usage') else 'No',
    )


def _health_score_prompt(repo: dict, tech: dict, data: dict) -> str:
    readme_analysis = data.get('readme_analysis', {})
    dockerfile = data.get('dockerfile_analysis', {})
    actions = data.get('actions_analysis', {})

    return HEALTH_SCORE_PROMPT.format(
        repo_name=repo.get('name', 'Unknown'),
        has_readme='Yes' if data.get('readme') else 'No',
        has_license='Yes' if data.get('license_info') else 'No',
        has_contributing='Yes' if data.get('contributing') else 'No',
        readme_sections=', '.join(readme_analysis.get('sections', [])) if readme_analysis.get('sections') else 'None',
        readme_quality=readme_analysis.get('quality_score', 0),
        has_badges='Yes' if readme_analysis.get('has_badges') else 'No',
        has_installation='Yes' if readme_analysis.get('has_installation') else 'No',
        has_usage='Yes' if readme_analysis.get('has_usage') else 'No',
        has_api_docs='Yes' if readme_analysis.get('has_api_reference') else 'No',
        has_examples='Yes' if readme_analysis.get('has_examples') else 'No',
        has_screenshots='Yes' if readme_analysis.get('has_screenshots') else 'No',
        has_contributing_guide='Yes' if readme_analysis.get('has_contributing') else 'No',
        has_dockerfile='Yes' if dockerfile.get('base_image') else 'No',
        has_ci='Yes' if actions.get('ci_type') and actions['ci_type'] != 'Unknown' else 'No',
        has_tests='Yes' if actions.get('test_framework') and actions['test_framework'] != 'Not detected' else 'No',
        has_healthcheck='Yes' if dockerfile.get('has_healthcheck') else 'No',
        has_multi_stage_build='Yes' if dockerfile.get('has_multi_stage_build') else 'No',
    )


def _suggestions_prompt(repo: dict, tech: dict, data: dict) -> str:
    readme_analysis = data.get('readme_analysis', {})
    dockerfile = data.get('dockerfile_analysis', {})
    actions = data.get('actions_analysis', {})

    missing = []
    if not readme_analysis.get('has_installation'):
        missing.append('Add an Installation section to the README')
    if not readme_analysis.get('has_usage'):
        missing.append('Add a Usage/Examples section to the README')
    if not readme_analysis.get('has_contributing'):
        missing.append('Add a Contributing guide')
    if not readme_analysis.get('has_api_reference'):
        missing.append('Add API documentation')
    if not readme_analysis.get('has_screenshots'):
        missing.append('Add screenshots or demos')
    if not data.get('license_info'):
        missing.append('Add a license file')
    if not dockerfile.get('base_image'):
        missing.append('Add a Dockerfile for containerization')
    if not actions.get('ci_type') or actions.get('ci_type') == 'Unknown':
        missing.append('Add CI/CD workflow')
    if not readme_analysis.get('has_badges'):
        missing.append('Add status badges to the README')
    if readme_analysis.get('word_count', 0) < 100:
        missing.append('Expand the README with more details')

    return SUGGESTIONS_PROMPT.format(
        repo_name=repo.get('name', 'Unknown'),
        tech_stack=', '.join(v for v in tech.values() if v and v != 'Not detected'),
        readme_quality=readme_analysis.get('quality_score', 0),
        health_score=data.get('readme_analysis', {}).get('quality_score', 0),
        missing_elements='; '.join(missing) if missing else 'All key elements are present',
    )