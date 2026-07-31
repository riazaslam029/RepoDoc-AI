import re
from typing import Dict, List, Optional


class DockerfileAnalyzer:
    def __init__(self, content: str):
        self.content = content
        self.lines = content.split('\n')

    def get_base_image(self) -> Optional[str]:
        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith('FROM'):
                parts = stripped.split()
                if len(parts) >= 2:
                    return parts[1]
        return None

    def get_exposed_ports(self) -> List[int]:
        ports = []
        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith('EXPOSE'):
                port_matches = re.findall(r'\d+', stripped)
                ports.extend(int(p) for p in port_matches)
        return ports

    def get_entrypoint(self) -> Optional[str]:
        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith('ENTRYPOINT'):
                return stripped
        return None

    def get_cmd(self) -> Optional[str]:
        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith('CMD'):
                return stripped
        return None

    def get_workdir(self) -> Optional[str]:
        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith('WORKDIR'):
                parts = stripped.split()
                if len(parts) >= 2:
                    return parts[1]
        return None

    def get_env_vars(self) -> Dict[str, str]:
        env_vars = {}
        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith('ENV'):
                parts = stripped[4:].strip()
                if '=' in parts:
                    key, value = parts.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"').strip("'")
        return env_vars

    def get_volumes(self) -> List[str]:
        volumes = []
        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith('VOLUME'):
                volume_matches = re.findall(r'["\']?([^"\'\s]+)["\']?', stripped)
                volumes.extend(v for v in volume_matches if v and v.upper() != 'VOLUME')
        return volumes

    def detect_language(self) -> str:
        content_lower = self.content.lower()
        base_image = (self.get_base_image() or '').lower()

        if any(x in base_image for x in ['node', 'nodejs']):
            return 'Node.js'
        if any(x in base_image for x in ['python', 'py']):
            return 'Python'
        if any(x in base_image for x in ['openjdk', 'java', 'jdk']):
            return 'Java'
        if any(x in base_image for x in ['golang', 'go']):
            return 'Go'
        if any(x in base_image for x in ['ruby', 'rails']):
            return 'Ruby'
        if any(x in base_image for x in ['php', 'apache', 'nginx']):
            return 'PHP'
        if any(x in base_image for x in ['rust', 'cargo']):
            return 'Rust'
        if any(x in base_image for x in ['dotnet', 'aspnet', 'mono']):
            return '.NET'
        if any(x in base_image for x in ['alpine', 'ubuntu', 'debian', 'centos']):
            return 'Generic Linux'
        return 'Unknown'

    def detect_framework(self) -> str:
        content_lower = self.content.lower()
        base_image = (self.get_base_image() or '').lower()

        if 'node' in base_image or 'node' in content_lower:
            if any(x in content_lower for x in ['next', 'nuxt', 'react', 'vue', 'angular', 'express', 'fastify', 'nest']):
                for fw in ['Next.js', 'Nuxt', 'React', 'Vue', 'Angular', 'Express', 'Fastify', 'NestJS']:
                    if fw.lower() in content_lower:
                        return fw
            return 'Node.js'

        if 'python' in base_image or 'python' in content_lower:
            if any(x in content_lower for x in ['django', 'flask', 'fastapi', 'flask', 'gunicorn', 'uvicorn']):
                for fw in ['Django', 'Flask', 'FastAPI', 'Gunicorn', 'Uvicorn']:
                    if fw.lower() in content_lower:
                        return fw
            return 'Python'

        if 'java' in base_image or 'openjdk' in base_image:
            if 'spring' in content_lower:
                return 'Spring Boot'
            return 'Java'

        if 'golang' in base_image or 'go' in base_image:
            return 'Go'

        return 'Not detected'

    def detect_database(self) -> str:
        content_lower = self.content.lower()
        indicators = {
            'PostgreSQL': ['postgres', 'postgresql'],
            'MySQL': ['mysql'],
            'MongoDB': ['mongo', 'mongodb'],
            'Redis': ['redis'],
            'SQLite': ['sqlite'],
            'Elasticsearch': ['elasticsearch'],
        }
        for db, keywords in indicators.items():
            for keyword in keywords:
                if keyword in content_lower:
                    return db
        return 'Not detected'

    def detect_deployment_target(self) -> str:
        content_lower = self.content.lower()
        if 'kubernetes' in content_lower or 'k8s' in content_lower:
            return 'Kubernetes'
        if 'docker' in content_lower or 'docker-compose' in content_lower:
            return 'Docker'
        if 'ecs' in content_lower or 'elastic beanstalk' in content_lower:
            return 'AWS ECS'
        if 'lambda' in content_lower or 'serverless' in content_lower:
            return 'AWS Lambda'
        if 'vercel' in content_lower:
            return 'Vercel'
        if 'heroku' in content_lower:
            return 'Heroku'
        return 'Docker Container'

    def has_multi_stage_build(self) -> bool:
        from_count = sum(1 for line in self.lines if line.strip().startswith('FROM'))
        return from_count > 1

    def has_healthcheck(self) -> bool:
        return any(line.strip().startswith('HEALTHCHECK') for line in self.lines)

    def analyze(self) -> Dict:
        return {
            'base_image': self.get_base_image(),
            'exposed_ports': self.get_exposed_ports(),
            'entrypoint': self.get_entrypoint(),
            'cmd': self.get_cmd(),
            'workdir': self.get_workdir(),
            'env_vars': self.get_env_vars(),
            'volumes': self.get_volumes(),
            'language': self.detect_language(),
            'framework': self.detect_framework(),
            'database': self.detect_database(),
            'deployment_target': self.detect_deployment_target(),
            'has_multi_stage_build': self.has_multi_stage_build(),
            'has_healthcheck': self.has_healthcheck(),
        }