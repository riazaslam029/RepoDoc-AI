import re
from typing import Dict, List, Optional


class ReadmeAnalyzer:
    def __init__(self, content: str):
        self.content = content
        self.lines = content.split('\n')

    def get_sections(self) -> List[str]:
        sections = []
        for line in self.lines:
            match = re.match(r'^#{1,6}\s+(.+)', line)
            if match:
                sections.append(match.group(1).strip())
        return sections

    def has_badges(self) -> bool:
        badge_patterns = [
            r'!\[.*?\]\(https?://.*?\)',
            r'\[!\[.*?\]\(https?://.*?\)\]',
        ]
        for pattern in badge_patterns:
            if re.search(pattern, self.content):
                return True
        return False

    def has_installation_section(self) -> bool:
        section_text = '\n'.join(self.lines).lower()
        indicators = ['installation', 'install', 'setup', 'getting started', 'quick start']
        return any(indicator in section_text for indicator in indicators)

    def has_usage_section(self) -> bool:
        section_text = '\n'.join(self.lines).lower()
        indicators = ['usage', 'example', 'quick example', 'demo']
        return any(indicator in section_text for indicator in indicators)

    def has_contributing_section(self) -> bool:
        section_text = '\n'.join(self.lines).lower()
        return 'contributing' in section_text

    def has_api_reference(self) -> bool:
        section_text = '\n'.join(self.lines).lower()
        indicators = ['api', 'endpoints', 'rest', 'graphql', 'swagger']
        return any(indicator in section_text for indicator in indicators)

    def has_examples(self) -> bool:
        section_text = '\n'.join(self.lines).lower()
        indicators = ['example', 'sample', 'tutorial', 'guide']
        return any(indicator in section_text for indicator in indicators)

    def has_screenshots(self) -> bool:
        return bool(re.search(r'!\[.*?\]\(.*?\)', self.content))

    def has_license_badge(self) -> bool:
        return bool(re.search(r'license.*badge|badge.*license', self.content, re.IGNORECASE))

    def word_count(self) -> int:
        return len(self.content.split())

    def code_blocks_count(self) -> int:
        return self.content.count('```')

    def has_table(self) -> bool:
        return bool(re.search(r'\|.*\|.*\|', self.content))

    def has_links(self) -> bool:
        return bool(re.search(r'\[.*?\]\(https?://', self.content))

    def get_heading_structure(self) -> Dict[str, int]:
        structure = {}
        for line in self.lines:
            match = re.match(r'^(#{1,6})\s+(.+)', line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                structure[f'h{level}'] = structure.get(f'h{level}', [])
                structure[f'h{level}'].append(title)
        return structure

    def analyze(self) -> Dict:
        return {
            'sections': self.get_sections(),
            'has_badges': self.has_badges(),
            'has_installation': self.has_installation_section(),
            'has_usage': self.has_usage_section(),
            'has_contributing': self.has_contributing_section(),
            'has_api_reference': self.has_api_reference(),
            'has_examples': self.has_examples(),
            'has_screenshots': self.has_screenshots(),
            'has_license_badge': self.has_license_badge(),
            'word_count': self.word_count(),
            'code_blocks_count': self.code_blocks_count(),
            'has_table': self.has_table(),
            'has_links': self.has_links(),
            'heading_structure': self.get_heading_structure(),
            'quality_score': self._calculate_quality_score(),
        }

    def _calculate_quality_score(self) -> int:
        score = 0
        if self.has_badges():
            score += 10
        if self.has_installation_section():
            score += 15
        if self.has_usage_section():
            score += 10
        if self.has_contributing_section():
            score += 10
        if self.has_api_reference():
            score += 10
        if self.has_examples():
            score += 10
        if self.has_screenshots():
            score += 10
        if self.has_table():
            score += 5
        if self.has_links():
            score += 5
        if self.word_count() > 100:
            score += 10
        if self.code_blocks_count() >= 2:
            score += 5
        if self.has_license_badge():
            score += 5
        return min(score, 100)