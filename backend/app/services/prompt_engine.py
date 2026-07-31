import os
from pathlib import Path
from typing import Optional
from app.services.bedrock_client import BedrockClient
from app.config import settings


bedrock = BedrockClient()
PROMPTS_DIR = Path(__file__).parent.parent.parent.parent / 'prompts'


def load_prompt(name: str) -> str:
    prompt_file = PROMPTS_DIR / f'{name}.md'
    if prompt_file.exists():
        return prompt_file.read_text()
    return f'# Prompt: {name}\n\nGenerate content for this repository.'


async def generate_documentation(repo_data: dict, doc_type: str) -> str:
    prompt = _build_prompt(doc_type, repo_data)
    if not prompt:
        return ''
    return await bedrock.generate(prompt)


def _build_prompt(doc_type: str, repo_data: dict) -> str:
    repo = repo_data.get('repository', {})
    tech = repo_data.get('tech_stack', {})
    readme_analysis = repo_data.get('readme_analysis', {})
    dockerfile = repo_data.get('dockerfile_analysis', {})
    actions = repo_data.get('actions_analysis', {})
    dependencies = repo_data.get('dependencies', {})

    prompt_template = load_prompt(doc_type)

    return prompt_template.format(
        repo_name=repo.get('name', 'Unknown'),
        description=repo.get('description') or 'No description',
        language=tech.get('language', 'Unknown'),
        framework=tech.get('framework', 'Unknown'),
        database=tech.get('database', 'Unknown'),
        deployment=tech.get('deployment', 'Unknown'),
        ci_cd=', '.join(tech.get('ci_cd', [])) if isinstance(tech.get('ci_cd'), list) else str(tech.get('ci_cd', '')),
        ai_libraries=', '.join(repo_data.get('ai_libraries', [])) if isinstance(repo_data.get('ai_libraries'), list) else 'None',
        topics=', '.join(repo.get('topics', [])),
        stars=repo.get('stargazers_count', 0),
        forks=repo.get('forks_count', 0),
        license=repo.get('license') or 'None',
        folder_structure=repo_data.get('folder_structure', 'N/A'),
        dependencies=', '.join(dependencies.get('all', [])) if isinstance(dependencies, dict) else '',
        python_deps=', '.join(dependencies.get('by_file', {}).get('requirements.txt', [])) if isinstance(dependencies, dict) else '',
        node_deps=', '.join(dependencies.get('by_file', {}).get('package.json', {}).get('dependencies', []) if isinstance(dependencies, dict) and isinstance(dependencies.get('by_file', {}).get('package.json'), dict) else []),
        tech_stack='\n'.join(f'- {k}: {v}' for k, v in tech.items() if v and v != 'Not detected'),
        readme_quality=readme_analysis.get('quality_score', 0),
        has_badges='Yes' if readme_analysis.get('has_badges') else 'No',
        has_installation='Yes' if readme_analysis.get('has_installation') else 'No',
        has_usage='Yes' if readme_analysis.get('has_usage') else 'No',
        has_contributing='Yes' if readme_analysis.get('has_contributing') else 'No',
        has_api_reference='Yes' if readme_analysis.get('has_api_reference') else 'No',
        has_examples='Yes' if readme_analysis.get('has_examples') else 'No',
        has_screenshots='Yes' if readme_analysis.get('has_screenshots') else 'No',
        has_contributing_guide='Yes' if readme_analysis.get('has_contributing') else 'No',
        has_dockerfile='Yes' if dockerfile.get('base_image') else 'No',
        docker_base_image=dockerfile.get('base_image') or 'N/A',
        docker_ports=dockerfile.get('exposed_ports', []),
        has_ci='Yes' if actions.get('ci_type') and actions['ci_type'] != 'Unknown' else 'No',
        ci_type=actions.get('ci_type', 'Unknown'),
        test_framework=actions.get('test_framework', 'Not detected'),
        has_deployment=actions.get('has_deployment_step', False),
        has_healthcheck='Yes' if dockerfile.get('has_healthcheck') else 'No',
        has_multi_stage_build='Yes' if dockerfile.get('has_multi_stage_build') else 'No',
    )