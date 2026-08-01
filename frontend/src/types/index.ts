export interface Repository {
  id: number;
  name: string;
  full_name: string;
  owner: string;
  description: string | null;
  html_url: string;
  stargazers_count: number;
  forks_count: number;
  language: string | null;
  created_at: string;
  updated_at: string;
  default_branch: string;
  topics: string[];
  license: string | null;
}

export interface AnalysisResult {
  repository?: Repository;
  tech_stack?: TechStack;
  folder_structure?: string;
  architecture_summary?: string;
  readme_content?: string;
  installation_guide?: string;
  api_documentation?: string;
  health_score?: HealthScore;
  suggestions?: string[];
}

export interface TechStack {
  language: string;
  framework: string;
  database: string;
  deployment: string;
  dependencies: string[];
  ai_libraries: string[];
  ci_cd: string[];
}

export interface HealthScore {
  overall: number;
  readme_quality: number;
  has_license: boolean;
  has_contributing: boolean;
  has_screenshots: boolean;
  has_api_docs: boolean;
  has_architecture: boolean;
  has_examples: boolean;
}

export interface AnalysisStatus {
  status: 'idle' | 'analyzing' | 'complete' | 'error';
  progress: number;
  message: string;
}