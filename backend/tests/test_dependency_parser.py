import pytest


dep_parser = pytest.importorskip('app.services.dependency_parser')
parse_requirements_txt = dep_parser.parse_requirements_txt
parse_package_json = dep_parser.parse_package_json
parse_pyproject_toml = dep_parser.parse_pyproject_toml
parse_dockerfile = dep_parser.parse_dockerfile
parse_docker_compose = dep_parser.parse_docker_compose
detect_ci_cd_from_files = dep_parser.detect_ci_cd_from_files


class TestParseRequirementsTxt:
    def test_parse_basic_requirements(self):
        content = "fastapi==0.111.0\nuvicorn==0.30.1\nhttpx==0.27.0"
        result = parse_requirements_txt(content)
        assert "fastapi" in result
        assert "uvicorn" in result
        assert "httpx" in result

    def test_parse_with_comments(self):
        content = "# This is a comment\nfastapi==0.111.0\n# Another comment"
        result = parse_requirements_txt(content)
        assert "fastapi" in result
        assert len(result) == 1

    def test_parse_empty(self):
        result = parse_requirements_txt("")
        assert result == []

    def test_parse_with_flags(self):
        content = "fastapi==0.111.0\n--extra-index-url https://example.com\nuvicorn==0.30.1"
        result = parse_requirements_txt(content)
        assert "fastapi" in result
        assert "uvicorn" in result


class TestParsePackageJson:
    def test_parse_basic_package_json(self):
        content = '{"name": "test", "dependencies": {"react": "^18.0.0", "express": "^4.0.0"}}'
        result = parse_package_json(content)
        assert "react" in result["dependencies"]
        assert "express" in result["dependencies"]
        assert result["framework"] == "React"

    def test_parse_nextjs(self):
        content = '{"dependencies": {"next": "^14.0.0", "react": "^18.0.0"}}'
        result = parse_package_json(content)
        assert result["framework"] == "Next.js"

    def test_parse_empty_package_json(self):
        content = '{"name": "test"}'
        result = parse_package_json(content)
        assert result["dependencies"] == []
        assert result["framework"] == "Not detected"


class TestParsePyprojectToml:
    def test_parse_basic_pyproject(self):
        content = """[project]
name = "test"
dependencies = ["fastapi", "uvicorn"]

[tool.poetry]
name = "test"
"""
        result = parse_pyproject_toml(content)
        assert "fastapi" in result["dependencies"]
        assert result["framework"] == "Poetry"

    def test_parse_django_pyproject(self):
        content = """[project]
name = "test"
dependencies = ["django", "djangorestframework"]
"""
        result = parse_pyproject_toml(content)
        assert result["framework"] == "Django"


class TestParseDockerfile:
    def test_parse_basic_dockerfile(self):
        content = """FROM node:18-alpine
WORKDIR /app
COPY package.json .
RUN npm install
EXPOSE 3000
CMD ["npm", "start"]"""
        result = parse_dockerfile(content)
        assert result["base_image"] == "node:18-alpine"
        assert "3000" in result["exposed_ports"]
        assert result["deployment"] == "Node.js Docker"

    def test_parse_python_dockerfile(self):
        content = """FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]"""
        result = parse_dockerfile(content)
        assert result["deployment"] == "Python Docker"

    def test_parse_multistage_dockerfile(self):
        content = """FROM node:18 as builder
WORKDIR /app
COPY package.json .
RUN npm install

FROM node:18-alpine
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000"""
        result = parse_dockerfile(content)
        assert result["base_image"] == "node:18-alpine"


class TestParseDockerCompose:
    def test_parse_basic_compose(self):
        content = """
version: '3'
services:
  web:
    build: .
    ports:
      - "8000:8000"
  db:
    image: postgres:15
"""
        result = parse_docker_compose(content)
        assert result["has_compose"] is True
        assert "web" in result["services"]
        assert "db" in result["services"]


class TestDetectCiCdFromFiles:
    def test_detect_github_actions(self):
        files = {
            ".github/workflows/ci.yml": "name: CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest",
        }
        result = detect_ci_cd_from_files(files)
        assert "GitHub Actions" in result

    def test_no_ci_cd(self):
        files = {}
        result = detect_ci_cd_from_files(files)
        assert result == []