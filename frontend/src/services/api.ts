import axios from 'axios';
import { AnalysisResult } from '../types';
import { validateGitHubUrl } from '../utils/validation';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
      return Promise.reject(new Error(message));
    }
    if (error.request) {
      return Promise.reject(new Error('Network error. Please check your connection.'));
    }
    return Promise.reject(new Error('An unexpected error occurred'));
  },
);

export const validateRepoUrl = async (url: string): Promise<{ valid: boolean; error?: string; owner?: string; repo?: string }> => {
  const validation = validateGitHubUrl(url);
  if (!validation.valid) {
    return validation;
  }
  try {
    const response = await api.post('/v1/validate', { repo_url: url });
    return response.data;
  } catch {
    return validation;
  }
};

export const analyzeRepository = async (repoUrl: string): Promise<AnalysisResult> => {
  const response = await api.post('/api/v1/analyze', { repo_url: repoUrl });
  return response.data;
};

export const downloadReadme = async (content: string): Promise<void> => {
  const blob = new Blob([content], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'README.md';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export default api;