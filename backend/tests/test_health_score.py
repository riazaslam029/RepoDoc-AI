import pytest
from app.services.health_score import HealthScorer


class TestHealthScorer:
    def test_compute_overall_with_all_good(self):
        repo_data = {
            'repository': {'name': 'test-repo'},
            'readme_analysis': {
                'quality_score': 90,
                'has_badges': True,
                'has_installation': True,
                'has_usage': True,
                'has_contributing': True,
                'has_api_reference': True,
                'has_examples': True,
                'has_screenshots': True,
                'word_count': 500,
                'code_blocks_count': 5,
            },
            'dockerfile_analysis': {'base_image': 'python:3.12'},
            'actions_analysis': {'ci_type': 'GitHub Actions', 'test_framework': 'pytest'},
            'license_info': {'spdx_id': 'MIT'},
            'contributing': '# Contributing',
            'readme': '# Test Repo',
        }
        scorer = HealthScorer(repo_data)
        result = scorer.compute_overall()
        assert result['overall'] > 0
        assert result['has_license'] is True
        assert result['has_contributing'] is True
        assert result['has_screenshots'] is True
        assert result['has_api_docs'] is True
        assert result['has_architecture'] is True
        assert result['has_examples'] is True

    def test_compute_overall_with_minimal(self):
        repo_data = {
            'repository': {'name': 'test-repo'},
            'readme_analysis': {
                'quality_score': 10,
                'has_badges': False,
                'has_installation': False,
                'has_usage': False,
                'has_contributing': False,
                'has_api_reference': False,
                'has_examples': False,
                'has_screenshots': False,
                'word_count': 50,
                'code_blocks_count': 0,
            },
            'dockerfile_analysis': {},
            'actions_analysis': {},
            'license_info': None,
            'contributing': None,
            'readme': '',
        }
        scorer = HealthScorer(repo_data)
        result = scorer.compute_overall()
        assert result['overall'] == 0

    def test_get_suggestions_with_missing_elements(self):
        repo_data = {
            'repository': {'name': 'test-repo'},
            'readme_analysis': {
                'quality_score': 10,
                'has_badges': False,
                'has_installation': False,
                'has_usage': False,
                'has_contributing': False,
                'has_api_reference': False,
                'has_examples': False,
                'has_screenshots': False,
                'word_count': 50,
                'code_blocks_count': 0,
            },
            'dockerfile_analysis': {},
            'actions_analysis': {},
            'license_info': None,
            'contributing': None,
            'readme': '',
        }
        scorer = HealthScorer(repo_data)
        suggestions = scorer.get_suggestions()
        assert len(suggestions) > 0
        assert any('Installation' in s for s in suggestions)
        assert any('license' in s.lower() for s in suggestions)

    def test_score_readme_quality(self):
        repo_data = {
            'repository': {'name': 'test-repo'},
            'readme_analysis': {
                'quality_score': 85,
                'has_badges': True,
                'has_installation': True,
                'has_usage': True,
                'has_contributing': True,
                'has_api_reference': True,
                'has_examples': True,
                'has_screenshots': True,
                'word_count': 500,
                'code_blocks_count': 5,
            },
            'dockerfile_analysis': {},
            'actions_analysis': {},
            'license_info': None,
            'contributing': None,
            'readme': '',
        }
        scorer = HealthScorer(repo_data)
        score = scorer.score_readme_quality()
        assert score > 0

    def test_score_license(self):
        repo_data = {
            'repository': {'name': 'test-repo'},
            'readme_analysis': {},
            'dockerfile_analysis': {},
            'actions_analysis': {},
            'license_info': {'spdx_id': 'MIT'},
            'contributing': None,
            'readme': '',
        }
        scorer = HealthScorer(repo_data)
        assert scorer.score_license() == 100

    def test_score_license_missing(self):
        repo_data = {
            'repository': {'name': 'test-repo'},
            'readme_analysis': {},
            'dockerfile_analysis': {},
            'actions_analysis': {},
            'license_info': None,
            'contributing': None,
            'readme': '',
        }
        scorer = HealthScorer(repo_data)
        assert scorer.score_license() == 0