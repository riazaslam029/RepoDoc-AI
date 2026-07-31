import re
from typing import Optional


def parse_requirements_txt(content: str) -> list[str]:
    dependencies = []
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('-'):
            continue
        match = re.match(r'^([a-zA-Z0-9_-]+)', line)
        if match:
            dependencies.append(match.group(1))
    return dependencies[:20]


def parse_package_json(content: str) -> dict:
    try:
        import json
        data = json.loads(content)
        deps = []
        for field in ['dependencies', 'devDependencies', 'peerDependencies']:
            if field in data and isinstance(data[field], dict):
                for pkg in list(data[field].keys())[:20]:
                    deps.append(pkg)
        return {
            'dependencies': deps,
            'scripts': list(data.get('scripts', {}).keys())[:10],
            'framework': _detect_framework_from_package_json(data),
        }
    except (json.JSONDecodeError, Exception):
        return {'dependencies': [], 'scripts': [], 'framework': 'Not detected'}


def _detect_framework_from_package_json(data: dict) -> str:
    deps = set()
    for field in ['dependencies', 'devDependencies', 'peerDependencies']:
        if field in data and isinstance(data[field], dict):
            deps.update(data[field].keys())

    framework_indicators = {
        'Next.js': {'next', 'next.js'},
        'React': {'react', 'react-dom'},
        'Vue.js': {'vue', 'vue-router', 'vuex', 'nuxt'},
        'Angular': {'@angular/core', '@angular/cli'},
        'Svelte': {'svelte', '@sveltejs/kit'},
        'Astro': {'astro'},
        'Remix': {'@remix-run'},
        'Nuxt': {'nuxt', 'nuxt3'},
        'Electron': {'electron'},
        'Tauri': {'@tauri-apps'},
        'Express': {'express'},
        'Fastify': {'fastify'},
        'NestJS': {'@nestjs'},
        'Django': {'django'},
        'Flask': {'flask'},
        'FastAPI': {'fastapi'},
        'Spring Boot': {'spring-boot'},
        'Rails': {'rails'},
        'Laravel': {'laravel'},
    }

    for framework, indicators in framework_indicators.items():
        if indicators & deps:
            return framework

    return 'Not detected'


def parse_pyproject_toml(content: str) -> dict:
    dependencies = []
    framework = 'Not detected'

    project_match = re.search(r'\[project\]', content)
    if project_match:
        section = content[project_match.end():]
        next_section = re.search(r'\n\[', section)
        if next_section:
            section = section[:next_section.start()]

        # Parse dependencies list
        deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', section, re.DOTALL)
        if deps_match:
            deps_content = deps_match.group(1)
            for dep in re.findall(r'"([^"]+)"', deps_content):
                dependencies.append(dep)
            for dep in re.findall(r"'([^']+)'", deps_content):
                dependencies.append(dep)

    framework_indicators = {
        'Django': ['django'],
        'Flask': ['flask'],
        'FastAPI': ['fastapi'],
        'Pyramid': ['pyramid'],
        'Celery': ['celery'],
        'SQLAlchemy': ['sqlalchemy'],
        'Pydantic': ['pydantic'],
        'Poetry': ['poetry'],
    }

    for fw, indicators in framework_indicators.items():
        for indicator in indicators:
            if indicator in content.lower():
                framework = fw
                break

    return {'dependencies': dependencies[:20], 'framework': framework}


def parse_dockerfile(content: str) -> dict:
    base_image = ''
    exposed_ports = []
    entrypoint = ''
    cmd = ''

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('FROM'):
            base_image = line.split()[1] if len(line.split()) > 1 else ''
        elif line.startswith('EXPOSE'):
            ports = re.findall(r'\d+', line)
            exposed_ports.extend(ports)
        elif line.startswith('ENTRYPOINT'):
            entrypoint = line
        elif line.startswith('CMD'):
            cmd = line

    deployment = 'Docker'
    if base_image:
        if 'node' in base_image.lower():
            deployment = 'Node.js Docker'
        elif 'python' in base_image.lower():
            deployment = 'Python Docker'
        elif 'java' in base_image.lower():
            deployment = 'Java Docker'
        elif 'golang' in base_image.lower() or 'go' in base_image.lower():
            deployment = 'Go Docker'

    return {
        'base_image': base_image,
        'exposed_ports': exposed_ports,
        'entrypoint': entrypoint,
        'cmd': cmd,
        'deployment': deployment,
    }


def parse_docker_compose(content: str) -> dict:
    try:
        import yaml
        data = yaml.safe_load(content)
        services = list(data.get('services', {}).keys()) if isinstance(data, dict) else []
        return {'services': services, 'has_compose': True}
    except Exception:
        return {'services': [], 'has_compose': False}


def parse_github_actions(content: str) -> dict:
    try:
        import yaml
        data = yaml.safe_load(content)
        jobs = list(data.get('jobs', {}).keys()) if isinstance(data, dict) else []
        triggers = list(data.get('on', {}).keys()) if isinstance(data.get('on'), dict) else []
        if isinstance(data.get('on'), str):
            triggers = [data.get('on')]
        return {'jobs': jobs, 'triggers': triggers, 'has_actions': True}
    except Exception:
        return {'jobs': [], 'triggers': [], 'has_actions': False}


def detect_ci_cd_from_files(file_contents: dict) -> list[str]:
    ci_cd = []
    for path, content in file_contents.items():
        if 'github/workflows' in path and content:
            result = parse_github_actions(content)
            if result.get('has_actions'):
                ci_cd.append('GitHub Actions')
        if path == 'docker-compose.yml' and content:
            result = parse_docker_compose(content)
            if result.get('has_compose'):
                ci_cd.append('Docker Compose')
    return ci_cd