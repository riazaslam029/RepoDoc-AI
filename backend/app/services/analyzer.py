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
from app.services.readme_analyzer import ReadmeAnalyzer
from app.services.dockerfile_analyzer import DockerfileAnalyzer
from app.services.actions_analyzer import GithubActionsAnalyzer
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

        readme_analysis = self._analyze_readme(readme)
        dockerfile_analysis = self._analyze_dockerfile(file_contents)
        actions_analysis = self._analyze_actions(file_contents, workflows)
        tech_stack = self._detect_tech_stack(tree, languages, repo_data, file_contents, dockerfile_analysis)
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
            'readme_analysis': readme_analysis,
            'dockerfile_analysis': dockerfile_analysis,
            'actions_analysis': actions_analysis,
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

    def _analyze_readme(self, readme: Optional[str]) -> Dict:
        if not readme:
            return {
                'sections': [],
                'has_badges': False,
                'has_installation': False,
                'has_usage': False,
                'has_contributing': False,
                'has_api_reference': False,
                'has_examples': False,
                'has_screenshots': False,
                'has_license_badge': False,
                'word_count': 0,
                'code_blocks_count': 0,
                'has_table': False,
                'has_links': False,
                'heading_structure': {},
                'quality_score': 0,
            }
        analyzer = ReadmeAnalyzer(readme)
        return analyzer.analyze()

    def _analyze_dockerfile(self, file_contents: Dict[str, str]) -> Dict:
        for path, content in file_contents.items():
            if path == 'Dockerfile':
                analyzer = DockerfileAnalyzer(content)
                return analyzer.analyze()
        return {
            'base_image': None,
            'exposed_ports': [],
            'entrypoint': None,
            'cmd': None,
            'workdir': None,
            'env_vars': {},
            'volumes': [],
            'language': 'Not detected',
            'framework': 'Not detected',
            'database': 'Not detected',
            'deployment_target': 'Not detected',
            'has_multi_stage_build': False,
            'has_healthcheck': False,
        }

    def _analyze_actions(self, file_contents: Dict[str, str], workflows: list) -> Dict:
        for path, content in file_contents.items():
            if 'github/workflows' in path and content:
                analyzer = GithubActionsAnalyzer(content)
                return analyzer.analyze()
        return {
            'triggers': [],
            'jobs': [],
            'run_steps': [],
            'actions': [],
            'ci_type': 'Unknown',
            'test_framework': 'Not detected',
            'has_deployment_step': False,
            'job_count': 0,
            'step_count': 0,
        }

    def _detect_tech_stack(self, tree: dict, languages: dict, repo_data: dict, file_contents: dict, dockerfile_analysis: dict) -> dict:
        files = tree.get('tree', [])
        file_names = [f['path'] for f in files]

        language = repo_data.get('language') or self._detect_primary_language(languages)
        framework = self._detect_framework(file_names, file_contents, dockerfile_analysis)
        database = self._detect_database(file_names, file_contents, dockerfile_analysis)
        deployment = self._detect_deployment(file_names, file_contents, dockerfile_analysis)
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

    def _detect_framework(self, file_names: list[str], file_contents: dict, dockerfile_analysis: dict) -> str:
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

        docker_fw = dockerfile_analysis.get('framework')
        if docker_fw and docker_fw != 'Not detected':
            return docker_fw

        return 'Not detected'

    def _detect_database(self, file_names: list[str], file_contents: dict, dockerfile_analysis: dict) -> str:
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

        docker_db = dockerfile_analysis.get('database')
        if docker_db and docker_db != 'Not detected':
            return docker_db

        for path, content in file_contents.items():
            content_lower = content.lower()
            for db, keywords in db_indicators.items():
                for keyword in keywords:
                    if keyword in content_lower:
                        return db

        return 'Not detected'

    def _detect_deployment(self, file_names: list[str], file_contents: dict, dockerfile_analysis: dict) -> str:
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

        docker_deploy = dockerfile_analysis.get('deployment_target')
        if docker_deploy and docker_deploy != 'Not detected':
            return docker_deploy

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

    def _build_folder_structure(self, tree: dict) -> str:
        files = tree.get('tree', [])
        folders = set()
        for f in files:
            if f['type'] == 'tree':
                folders.add(f['path'])

        lines = ['📁 root/']
        sorted_folders = sorted(folders)
        for folder in sorted_folders[:30]:
            depth = folder.count('/')
            indent = '  ' * depth
            name = folder.split('/')[-1]
            lines.append(f'{indent}📁 {name}/')

        for f in files:
            if f['type'] == 'blob' and f['path'] not in [fl.split('/')[-1] for fl in lines]:
                depth = f['path'].count('/')
                if depth <= 2:
                    indent = '  ' * depth
                    lines.append(f'{indent}📄 {f["path"]}')

        return '\n'.join(lines[:50])