import re
from typing import Optional
from app.services.github_client import GitHubClient
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

        tech_stack = self._detect_tech_stack(tree, languages, repo_data)
        folder_structure = self._build_folder_structure(tree)

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
            },
            'tech_stack': tech_stack,
            'folder_structure': folder_structure,
            'readme': readme,
            'license_info': license_info,
            'contributing': contributing,
            'workflows': workflows,
            'tree': tree,
        }

    def _parse_url(self, url: str) -> tuple[str, str]:
        pattern = r'github\.com/([^/]+)/([^/]+)'
        match = re.search(pattern, url)
        if not match:
            raise ValueError(f'Invalid GitHub URL: {url}')
        return match.group(1), match.group(2).replace('.git', '')

    def _detect_tech_stack(self, tree: dict, languages: dict, repo_data: dict) -> dict:
        files = tree.get('tree', [])
        file_names = [f['path'] for f in files]

        language = repo_data.get('language') or self._detect_primary_language(languages)
        framework = self._detect_framework(file_names)
        database = self._detect_database(file_names)
        deployment = self._detect_deployment(file_names)
        dependencies = self._detect_dependencies(file_names, files)
        ai_libraries = self._detect_ai_libraries(file_names, files)
        ci_cd = self._detect_ci_cd(file_names)

        return {
            'language': language,
            'framework': framework,
            'database': database,
            'deployment': deployment,
            'dependencies': dependencies,
            'ai_libraries': ai_libraries,
            'ci_cd': ci_cd,
        }

    def _detect_primary_language(self, languages: dict) -> str:
        if not languages:
            return 'Unknown'
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        return sorted_langs[0][0]

    def _detect_framework(self, file_names: list[str]) -> str:
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

    def _detect_deployment(self, file_names: list[str]) -> str:
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
        return 'Not detected'

    def _detect_dependencies(self, file_names: list[str], files: list) -> list[str]:
        deps = []
        dep_files = {
            'requirements.txt': 'Python',
            'Pipfile': 'Python',
            'pyproject.toml': 'Python',
            'setup.py': 'Python',
            'package.json': 'Node.js',
            'Gemfile': 'Ruby',
            'go.mod': 'Go',
            'Cargo.toml': 'Rust',
            'pom.xml': 'Java',
            'build.gradle': 'Java',
            'composer.json': 'PHP',
        }

        for fn, lang in dep_files.items():
            if any(fn in f for f in file_names):
                deps.append(f'{lang} ({fn})')

        return deps

    def _detect_ai_libraries(self, file_names: list[str], files: list) -> list[str]:
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
        for lib, indicators in ai_indicators.items():
            for indicator in indicators:
                if any(indicator.lower() in fn.lower() for fn in file_names):
                    detected.append(lib)
                    break

        return detected

    def _detect_ci_cd(self, file_names: list[str]) -> list[str]:
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
        return ci_cd

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