import os
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent.parent.parent / 'prompts'


def load_prompt(name: str) -> str:
    prompt_file = PROMPTS_DIR / f'{name}.md'
    if prompt_file.exists():
        return prompt_file.read_text()
    return f'# Prompt: {name}\n\nGenerate content for this repository.'


README_PROMPT = """You are a technical documentation expert. Analyze the following GitHub repository and generate a professional README.md file.

Repository: {repo_name}
Description: {description}
Language: {language}
Topics: {topics}
Stars: {stars}
License: {license}

Tech Stack:
{tech_stack}

Folder Structure:
{folder_structure}

Dependencies:
{dependencies}

CI/CD:
{ci_cd}

Write a comprehensive README.md that includes:
1. Project title and description
2. Features list
3. Tech stack
4. Installation instructions
5. Usage examples
6. Contributing guidelines
7. License information
8. Links and references

The README should be professional, well-structured, and follow best practices for open-source projects."""

INSTALLATION_PROMPT = """Analyze the following repository and generate clear installation instructions.

Repository: {repo_name}
Tech Stack: {tech_stack}
Dependencies: {dependencies}
Folder Structure:
{folder_structure}

Generate step-by-step installation instructions covering:
1. Prerequisites
2. Installation steps
3. Configuration
4. Running the project
5. Common issues and troubleshooting

Be specific and include exact commands where applicable."""

ARCHITECTURE_PROMPT = """Analyze the following repository and provide an architecture summary.

Repository: {repo_name}
Language: {language}
Framework: {framework}
Database: {database}
Deployment: {deployment}
Folder Structure:
{folder_structure}

Provide a concise architecture summary covering:
1. Overall architecture pattern
2. Key components and their responsibilities
3. Data flow
4. External integrations
5. Scalability considerations

Keep it concise and informative."""

API_DOC_PROMPT = """Analyze the following repository and document any API endpoints.

Repository: {repo_name}
Language: {language}
Framework: {framework}
Folder Structure:
{folder_structure}

Identify and document:
1. API endpoints (method, path, description)
2. Request/response formats
3. Authentication methods
4. Error handling
5. Rate limiting if applicable

If no API endpoints are detected, state that clearly."""

HEALTH_SCORE_PROMPT = """Evaluate the documentation health of this repository.

Repository: {repo_name}
Has README: {has_readme}
Has License: {has_license}
Has Contributing Guide: {has_contributing}
Has README with sections: {readme_sections}
Has Examples: {has_examples}
Has API Documentation: {has_api_docs}
Has Architecture Docs: {has_architecture}
Has Screenshots: {has_screenshots}

Score each category out of 100 and provide an overall score.
Also provide specific suggestions for improvement."""

SUGGESTIONS_PROMPT = """Based on the following repository analysis, provide actionable suggestions to improve the documentation.

Repository: {repo_name}
Tech Stack: {tech_stack}
Current README Quality: {readme_quality}
Health Score: {health_score}
Missing Elements: {missing_elements}

Provide 5-8 specific, actionable suggestions to improve the project documentation. Prioritize high-impact, low-effort improvements."""