import re
from typing import Dict, List, Optional


class GithubActionsAnalyzer:
    def __init__(self, content: str):
        self.content = content

    def get_triggers(self) -> List[str]:
        triggers = []
        on_match = re.search(r'on:\s*(.+)', self.content, re.DOTALL)
        if on_match:
            on_content = on_match.group(1)
            if 'push' in on_content:
                triggers.append('push')
            if 'pull_request' in on_content:
                triggers.append('pull_request')
            if 'schedule' in on_content:
                triggers.append('schedule')
            if 'workflow_dispatch' in on_content:
                triggers.append('workflow_dispatch')
            if 'release' in on_content:
                triggers.append('release')
        return triggers

    def get_jobs(self) -> List[Dict[str, str]]:
        jobs = []
        jobs_match = re.search(r'jobs:\s*(.+)', self.content, re.DOTALL)
        if jobs_match:
            jobs_content = jobs_match.group(1)
            job_names = re.findall(r'^\s{2}(\w[\w-]*):', jobs_content, re.MULTILINE)
            for job_name in job_names:
                jobs.append({'name': job_name})
        return jobs

    def get_run_steps(self) -> List[str]:
        steps = []
        step_matches = re.findall(r'run:\s*["\']?(.+?)["\']?\s*$', self.content, re.MULTILINE)
        for step in step_matches:
            clean_step = step.strip().strip('"').strip("'")
            if clean_step and len(clean_step) > 2:
                steps.append(clean_step)
        return steps[:20]

    def get_actions(self) -> List[str]:
        actions = []
        action_matches = re.findall(r'uses:\s*(.+)', self.content)
        for action in action_matches:
            clean = action.strip().strip('"').strip("'")
            if clean:
                actions.append(clean)
        return actions[:20]

    def detect_ci_type(self) -> str:
        triggers = self.get_triggers()
        jobs = self.get_jobs()

        if 'pull_request' in triggers and 'push' in triggers:
            return 'CI'
        if 'release' in triggers:
            return 'CD'
        if len(jobs) > 3:
            return 'Complex CI/CD'
        if triggers:
            return 'CI'
        return 'Unknown'

    def detect_test_framework(self) -> str:
        content_lower = self.content.lower()
        frameworks = {
            'Jest': 'jest',
            'pytest': 'pytest',
            'Mocha': 'mocha',
            'JUnit': 'junit',
            'Go test': 'go test',
            'RSpec': 'rspec',
            'PHPUnit': 'phpunit',
            'NUnit': 'nunit',
            'Cypress': 'cypress',
            'Playwright': 'playwright',
        }
        for fw, keyword in frameworks.items():
            if keyword in content_lower:
                return fw
        return 'Not detected'

    def detect_deployment_step(self) -> bool:
        content_lower = self.content.lower()
        deploy_keywords = ['deploy', 'release', 'push to', 'docker push', 'helm', 'terraform', 'aws s3', 'vercel', 'netlify']
        return any(kw in content_lower for kw in deploy_keywords)

    def analyze(self) -> Dict:
        return {
            'triggers': self.get_triggers(),
            'jobs': self.get_jobs(),
            'run_steps': self.get_run_steps(),
            'actions': self.get_actions(),
            'ci_type': self.detect_ci_type(),
            'test_framework': self.detect_test_framework(),
            'has_deployment_step': self.detect_deployment_step(),
            'job_count': len(self.get_jobs()),
            'step_count': len(self.get_run_steps()),
        }