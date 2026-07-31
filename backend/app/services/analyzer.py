import re
from typing import Optional, Dict, Any
from app.services.github_client import GitHubClient
from app.services.dependency_parser import (
    parse_requirements_txt,
    parse_package_json,
    parse_pyproject_toml,
    parse_dockerfile,
    parse_docker_compose,
    detect_ci_cd_from_files,
)
from app.config import settings


class RepositoryAnalyzer:
    def __init__(self):
        self.github = GitHubClient()

    async def analyze(self, repo_url: str) -> dict:
        owner, repo = self._parse_url(repo_url)
        repo_data = await self.github.get_repository(owner, repo)
        languages = await self.github.get_languages(owner, repo)
        readme = await self.github.get_readme(owner, repo)
        tree = await self.github.get_tree(owner, repo, repo_data.get('default_branch', 'main'))
        license_info = await self.github.get_license(owner, repo)
        contributing = await self.github.get_contributing(owner, repo)
        workflows = await self.github.get_workflows(owner, repo)

        file_contents = await self._fetch_key_file_contents(owner, repo, tree)

        tech_stack = self._detect_tech_stack(tree, languages, repo_data, file_contents)
        folder_structure = self._build_folder_structure(tree)
        dependencies = self._parse_dependencies(file_contents)
        ai_libraries = self._detect_ai_libraries(tree.get('tree', []), file_contents)

        return {
            'repository': {
                'id': repo_data.get('id'),
                'name': repo_data.get('name'),
                'full_name': repo_data.get('full_name'),
                'owner': repo_data.get('owner', {}).get('login'),
                'description': repo_data.get('description'),
                'html_url': repo_data.get('html_url'),
                'stargazers_count': repo_data.get('stargazers_count', 0),
                'forks_count': repo_data.get('forks_count', 0),
                'language': repo_data.get('language'),
                'created_at': repo_data.get('created_at'),
                'updated_at': repo_data.get('updated_at'),
                'default_branch': repo_data.get('default_branch'),
                'topics': repo_data.get('topics', []),
                'license': repo_data.get('license', {}).get('spdx_id') if repo_data.get('license') else None,
                'private': repo_data.get('private', False),
                'archived': repo_data.get('archived', False),
                'has_issues': repo_data.get('has_issues', False),
                'has_wiki': repo_data.get('has_wiki', False),
                'has_pages': repo_data.get('has_pages', False),
                'forks': repo_data.get('forks_count', 0),
                'open_issues': repo_data.get('open_issues_count', 0),
                'watchers': repo_data.get('watchers_count', 0),
            },
            'tech_stack': tech_stack,
            'folder_structure': folder_structure,
            'dependencies': dependencies,
            'readme': readme,
            'license_info': license_info,
            'contributing': contributing,
            'workflows': workflows,
            'tree': tree,
            'file_contents': file_contents,
            'ai_libraries': ai_libraries,
        }

    async def _fetch_key_file_contents(self, owner: str, repo: str, tree: dict) -> Dict[str, str]:
        files = tree.get('tree', [])
        key_files = [
            'requirements.txt', 'Pipfile', 'pyproject.toml', 'setup.py',
            'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
            'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            '.github/workflows/ci.yml', '.github/workflows/main.yml',
            '.github/workflows/build.yml', '.github/workflows/deploy.yml',
            'Gemfile', 'go.mod', 'Cargo.toml', 'pom.xml', 'build.gradle',
            'composer.json', 'Makefile', 'terraform.tf',
        ]

        contents = {}
        for f in files:
            if f['path'] in key_files and f['type'] == 'blob':
                content = await self.github.get_file_content(owner, repo, f['path'])
                if content:
                    contents[f['path']] = content

        return contents

    def _parse_url(self, url: str) -> tuple[str, str]:
        pattern = r'github\.com/([^/]+)/([^/]+)'
        match = re.search(pattern, url)
        if not match:
            raise ValueError(f'Invalid GitHub URL: {url}')
        return match.group(1), match.group(2).replace('.git', '')

    def _detect_tech_stack(self, tree: dict, languages: dict, repo_data: dict, file_contents: dict) -> dict:
        files = tree.get('tree', [])
        file_names = [f['path'] for f in files]

        language = repo_data.get('language') or self._detect_primary_language(languages)
        framework = self._detect_framework(file_names, file_contents)
        database = self._detect_database(file_names)
        deployment = self._detect_deployment(file_names, file_contents)
        ci_cd = self._detect_ci_cd(file_names, file_contents)

        return {
            'language': language,
            'framework': framework,
            'database': database,
            'deployment': deployment,
            'ci_cd': ci_cd,
        }

    def _detect_primary_language(self, languages: dict) -> str:
        if not languages:
            return 'Unknown'
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        return sorted_langs[0][0]

    def _detect_framework(self, file_names: list[str], file_contents: dict) -> str:
        framework_indicators = {
            'Next.js': ['next.config', 'pages/', 'app/'],
            'React': ['package.json'],
            'Vue.js': ['vue.config.js', 'vite.config.js'],
            'Django': ['manage.py', 'settings.py', 'urls.py'],
            'Flask': ['app.py', 'flask', 'wsgi.py'],
            'FastAPI': ['main.py', 'app/main.py'],
            'Express': ['server.js', 'app.js', 'express'],
            'Spring Boot': ['pom.xml', 'build.gradle'],
            'Rails': ['Gemfile', 'config/routes.rb'],
            'Laravel': ['artisan', 'composer.json'],
            'Docker': ['Dockerfile', 'docker-compose.yml'],
        }

        for fw, indicators in framework_indicators.items():
            for indicator in indicators:
                if any(indicator in fn for fn in file_names):
                    return fw

        for path, content in file_contents.items():
            if path == 'package.json':
                parsed = parse_package_json(content)
                if parsed.get('framework') and parsed['framework'] != 'Not detected':
                    return parsed['framework']
            if path == 'pyproject.toml':
                parsed = parse_pyproject_toml(content)
                if parsed.get('framework') and parsed['framework'] != 'Not detected':
                    return parsed['framework']

        return 'Not detected'

    def _detect_database(self, file_names: list[str]) -> str:
        db_indicators = {
            'PostgreSQL': ['postgresql', 'pg_'],
            'MySQL': ['mysql', '.sql'],
            'MongoDB': ['mongodb', 'mongo', 'mongoose'],
            'Redis': ['redis', '.redis'],
            'SQLite': ['sqlite', '.db', '.sqlite'],
            'Elasticsearch': ['elasticsearch', 'elasticsearch.yml'],
        }

        for db, indicators in db_indicators.items():
            for indicator in indicators:
                if any(indicator.lower() in fn.lower() for fn in file_names):
                    return db
        return 'Not detected'

    def _detect_deployment(self, file_names: list[str], file_contents: dict) -> str:
        deploy_indicators = {
            'AWS Lambda': ['lambda', 'serverless.yml', 'sam.json', 'cloudformation.yml'],
            'AWS ECS': ['Dockerfile', 'docker-compose.yml', 'ecs-task'],
            'Vercel': ['vercel.json', 'now.json'],
            'Netlify': ['netlify.toml', '_redirects'],
            'Heroku': ['Procfile', 'heroku.yml'],
            'Docker': ['Dockerfile', 'docker-compose.yml'],
            'Kubernetes': ['k8s/', 'kubernetes/', '.k8s/'],
            'GitHub Actions': ['.github/workflows/'],
        }

        for deploy, indicators in deploy_indicators.items():
            for indicator in indicators:
                if any(indicator in fn for fn in file_names):
                    return deploy

        for path, content in file_contents.items():
            if path == 'Dockerfile':
                parsed = parse_dockerfile(content)
                if parsed.get('deployment'):
                    return parsed['deployment']

        return 'Not detected'

    def _detect_ci_cd(self, file_names: list[str], file_contents: dict) -> list[str]:
        ci_cd = []
        if any('.github/workflows/' in fn for fn in file_names):
            ci_cd.append('GitHub Actions')
        if any('Jenkinsfile' in fn for fn in file_names):
            ci_cd.append('Jenkins')
        if any('.circleci/' in fn for fn in file_names):
            ci_cd.append('CircleCI')
        if any('.travis.yml' in fn for fn in file_names):
            ci_cd.append('Travis CI')
        if any('azure-pipelines.yml' in fn for fn in file_names):
            ci_cd.append('Azure Pipelines')

        ci_cd.extend(detect_ci_cd_from_files(file_contents))
        return list(set(ci_cd))

    def _parse_dependencies(self, file_contents: dict) -> dict:
        all_deps = []
        parsed_files = {}

        for path, content in file_contents.items():
            if path == 'requirements.txt':
                deps = parse_requirements_txt(content)
                if deps:
                    all_deps.extend(deps)
                    parsed_files['requirements.txt'] = deps
            elif path == 'package.json':
                parsed = parse_package_json(content)
                if parsed.get('dependencies'):
                    all_deps.extend(parsed['dependencies'])
                parsed_files['package.json'] = parsed
            elif path == 'pyproject.toml':
                parsed = parse_pyproject_toml(content)
                if parsed.get('dependencies'):
                    all_deps.extend(parsed['dependencies'])
                parsed_files['pyproject.toml'] = parsed

        return {'all': list(set(all_deps)), 'by_file': parsed_files}

    def _detect_ai_libraries(self, files: list, file_contents: dict) -> list[str]:
        ai_indicators = {
            'TensorFlow': ['tensorflow', 'tf.keras', 'tf_'],
            'PyTorch': ['torch', 'pytorch'],
            'Hugging Face': ['transformers', 'huggingface', 'datasets'],
            'LangChain': ['langchain', 'llama_index', 'openai'],
            'scikit-learn': ['sklearn', 'scikit-learn'],
            'OpenAI': ['openai', 'gpt', 'chatgpt'],
            'PyTorch Lightning': ['pytorch_lightning', 'lightning'],
        }

        detected = []
        file_names = [f['path'] for f in files]

        for lib, indicators in ai_indicators.items():
            for indicator in indicators:
                if any(indicator.lower() in fn.lower() for fn in file_names):
                    detected.append(lib)
                    break

        for path, content in file_contents.items():
            if path.endswith('.py') or path.endswith('.txt') or path.endswith('.toml'):
                content_lower = content.lower()
                for lib, indicators in ai_indicators.items():
                    if lib not in detected:
                        for indicator in indicators:
                            if indicator.lower() in content_lower:
                                detected.append(lib)
                                break

        return detected