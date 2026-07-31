from typing import Dict


class HealthScorer:
    def __init__(self, repo_data: dict):
        self.repo_data = repo_data
        self.readme_analysis = repo_data.get('readme_analysis', {})
        self.dockerfile = repo_data.get('dockerfile_analysis', {})
        self.actions = repo_data.get('actions_analysis', {})
        self.license_info = repo_data.get('license_info')
        self.contributing = repo_data.get('contributing')
        self.readme = repo_data.get('readme')

    def score_readme_quality(self) -> int:
        score = 0
        analysis = self.readme_analysis

        if analysis.get('has_badges'):
            score += 10
        if analysis.get('has_installation'):
            score += 15
        if analysis.get('has_usage'):
            score += 10
        if analysis.get('has_contributing'):
            score += 10
        if analysis.get('has_api_reference'):
            score += 10
        if analysis.get('has_examples'):
            score += 10
        if analysis.get('has_screenshots'):
            score += 10
        if analysis.get('has_table'):
            score += 5
        if analysis.get('has_links'):
            score += 5
        if analysis.get('word_count', 0) > 100:
            score += 10
        if analysis.get('code_blocks_count', 0) >= 2:
            score += 5
        if analysis.get('has_license_badge'):
            score += 5

        return min(score, 100)

    def score_license(self) -> int:
        return 100 if self.license_info else 0

    def score_contributing(self) -> int:
        return 100 if self.contributing else 0

    def score_screenshots(self) -> int:
        return 100 if self.readme_analysis.get('has_screenshots') else 0

    def score_api_docs(self) -> int:
        return 100 if self.readme_analysis.get('has_api_reference') else 0

    def score_architecture(self) -> int:
        score = 0
        if self.dockerfile.get('base_image'):
            score += 50
        if self.actions.get('ci_type') and self.actions['ci_type'] != 'Unknown':
            score += 50
        return min(score, 100)

    def score_examples(self) -> int:
        return 100 if self.readme_analysis.get('has_examples') else 0

    def compute_overall(self) -> Dict:
        readme_quality = self.score_readme_quality()
        has_license = self.score_license() > 0
        has_contributing = self.score_contributing() > 0
        has_screenshots = self.score_screenshots() > 0
        has_api_docs = self.score_api_docs() > 0
        has_architecture = self.score_architecture() > 0
        has_examples = self.score_examples() > 0

        weights = {
            'readme_quality': 0.35,
            'license': 0.10,
            'contributing': 0.10,
            'screenshots': 0.10,
            'api_docs': 0.10,
            'architecture': 0.15,
            'examples': 0.10,
        }

        overall = int(
            readme_quality * weights['readme_quality']
            + (100 if has_license else 0) * weights['license']
            + (100 if has_contributing else 0) * weights['contributing']
            + (100 if has_screenshots else 0) * weights['screenshots']
            + (100 if has_api_docs else 0) * weights['api_docs']
            + (100 if has_architecture else 0) * weights['architecture']
            + (100 if has_examples else 0) * weights['examples']
        )

        return {
            'overall': overall,
            'readme_quality': readme_quality,
            'has_license': has_license,
            'has_contributing': has_contributing,
            'has_screenshots': has_screenshots,
            'has_api_docs': has_api_docs,
            'has_architecture': has_architecture,
            'has_examples': has_examples,
        }

    def get_suggestions(self) -> list:
        suggestions = []
        analysis = self.readme_analysis

        if not analysis.get('has_installation'):
            suggestions.append('Add an Installation section to the README')
        if not analysis.get('has_usage'):
            suggestions.append('Add a Usage/Examples section to the README')
        if not analysis.get('has_contributing'):
            suggestions.append('Add a Contributing guide')
        if not analysis.get('has_api_reference'):
            suggestions.append('Add API documentation')
        if not analysis.get('has_screenshots'):
            suggestions.append('Add screenshots or demos')
        if not self.license_info:
            suggestions.append('Add a license file')
        if not self.contributing:
            suggestions.append('Add a CONTRIBUTING.md file')
        if not self.dockerfile.get('base_image'):
            suggestions.append('Add a Dockerfile for containerization')
        if not self.actions.get('ci_type') or self.actions.get('ci_type') == 'Unknown':
            suggestions.append('Add CI/CD workflow')
        if not analysis.get('has_badges'):
            suggestions.append('Add status badges to the README')
        if analysis.get('word_count', 0) < 100:
            suggestions.append('Expand the README with more details')

        return suggestions