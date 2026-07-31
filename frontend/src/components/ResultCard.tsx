import { useState } from 'react';
import { Repository, TechStack, HealthScore } from '../types';
import { DownloadIcon, CopyIcon, FolderIcon, ServerIcon, RocketIcon, ShieldCheckIcon, CheckCircleIcon } from './icons';
import { downloadReadme } from '../services/api';

interface ResultCardProps {
  repository: Repository;
  techStack: TechStack;
  folderStructure: string;
  architectureSummary: string;
  readmeContent: string;
  installationGuide: string;
  apiDocumentation: string;
  healthScore: HealthScore;
  suggestions: string[];
}

const ResultCard = ({
  repository,
  techStack,
  folderStructure,
  architectureSummary,
  readmeContent,
  installationGuide,
  apiDocumentation,
  healthScore,
  suggestions,
}: ResultCardProps) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'readme' | 'tech' | 'health'>('overview');
  const [copied, setCopied] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const handleCopyReadme = async () => {
    try {
      await navigator.clipboard.writeText(readmeContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      const textArea = document.createElement('textarea');
      textArea.value = readmeContent;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    downloadReadme(readmeContent);
  };

  const handleDownloadAll = () => {
    const allDocs = `# ${repository.name}\n\n${readmeContent}\n\n---\n\n## Installation Guide\n\n${installationGuide}\n\n---\n\n## Architecture\n\n${architectureSummary}\n\n---\n\n## API Documentation\n\n${apiDocumentation}\n\n---\n\n## Health Score\n\n${JSON.stringify(healthScore, null, 2)}\n\n---\n\n## Suggestions\n\n${suggestions.map(s => `- ${s}`).join('\n')}`;
    downloadReadme(allDocs);
  };

  const scoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 dark:text-green-400';
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const scoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-100 dark:bg-green-900/30';
    if (score >= 60) return 'bg-yellow-100 dark:bg-yellow-900/30';
    return 'bg-red-100 dark:bg-red-900/30';
  };

  return (
    <div className="space-y-6">
      <div className="card p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-2xl font-bold">{repository.name}</h2>
            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">{repository.full_name}</p>
          </div>
          <div className="flex gap-3 flex-wrap">
            <button onClick={handleDownloadAll} className="btn-secondary flex items-center gap-2 text-sm">
              <DownloadIcon className="w-4 h-4" />
              Download All
            </button>
            <button onClick={handleCopyReadme} className="btn-secondary flex items-center gap-2 text-sm">
              {copied ? <CheckCircleIcon className="w-4 h-4 text-green-500" /> : <CopyIcon className="w-4 h-4" />}
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button onClick={handleDownload} className="btn-primary flex items-center gap-2 text-sm">
              <DownloadIcon className="w-4 h-4" />
              Download
            </button>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-6">
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-brand-100 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300 text-sm font-medium">
            <ShieldCheckIcon className="w-4 h-4" />
            Health: {healthScore.overall}/100
          </span>
          {repository.language && (
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-sm">
              {repository.language}
            </span>
          )}
          {repository.stargazers_count > 0 && (
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-sm">
              ⭐ {repository.stargazers_count}
            </span>
          )}
        </div>

        <div className="flex gap-1 border-b border-gray-200 dark:border-gray-800 mb-6">
          {(['overview', 'readme', 'tech', 'health'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab
                  ? 'border-brand-600 text-brand-600 dark:text-brand-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        <div className="prose prose-sm dark:prose-invert max-w-none">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <RocketIcon className="w-5 h-5 text-brand-500" />
                  Project Overview
                </h3>
                <p className="text-gray-600 dark:text-gray-400">{repository.description || 'No description provided.'}</p>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <FolderIcon className="w-5 h-5 text-brand-500" />
                  Folder Structure
                </h3>
                <pre className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 text-sm overflow-x-auto font-mono">{folderStructure}</pre>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <ServerIcon className="w-5 h-5 text-brand-500" />
                  Architecture Summary
                </h3>
                <p className="text-gray-600 dark:text-gray-400 whitespace-pre-wrap">{architectureSummary}</p>
              </div>
            </div>
          )}

          {activeTab === 'readme' && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Generated README</h3>
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6 font-mono text-sm whitespace-pre-wrap border border-gray-200 dark:border-gray-800">
                {readmeContent}
              </div>
            </div>
          )}

          {activeTab === 'tech' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-3">Tech Stack</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                    <span className="text-xs uppercase tracking-wider text-gray-400 dark:text-gray-600">Language</span>
                    <p className="font-medium mt-1">{techStack.language || 'Not detected'}</p>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                    <span className="text-xs uppercase tracking-wider text-gray-400 dark:text-gray-600">Framework</span>
                    <p className="font-medium mt-1">{techStack.framework || 'Not detected'}</p>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                    <span className="text-xs uppercase tracking-wider text-gray-400 dark:text-gray-600">Database</span>
                    <p className="font-medium mt-1">{techStack.database || 'Not detected'}</p>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                    <span className="text-xs uppercase tracking-wider text-gray-400 dark:text-gray-600">Deployment</span>
                    <p className="font-medium mt-1">{techStack.deployment || 'Not detected'}</p>
                  </div>
                </div>
              </div>

              {techStack.dependencies.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Dependencies</h4>
                  <div className="flex flex-wrap gap-2">
                    {techStack.dependencies.map((dep, i) => (
                      <span key={i} className="px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-sm">{dep}</span>
                    ))}
                  </div>
                </div>
              )}

              {installationGuide && (
                <div>
                  <h3 className="text-lg font-semibold mb-3">Installation Guide</h3>
                  <pre className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 text-sm overflow-x-auto font-mono whitespace-pre-wrap">{installationGuide}</pre>
                </div>
              )}

              {apiDocumentation && (
                <div>
                  <h3 className="text-lg font-semibold mb-3">API Documentation</h3>
                  <pre className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 text-sm overflow-x-auto font-mono whitespace-pre-wrap">{apiDocumentation}</pre>
                </div>
              )}
            </div>
          )}

          {activeTab === 'health' && (
            <div className="space-y-6">
              <div className="text-center">
                <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full ${scoreBg(healthScore.overall)} ${scoreColor(healthScore.overall)} text-4xl font-extrabold mb-4`}>
                  {healthScore.overall}
                </div>
                <h3 className="text-lg font-semibold">Documentation Health Score</h3>
                <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Out of 100</p>
              </div>

              <div className="space-y-3">
                {[
                  { label: 'README Quality', value: healthScore.readme_quality, max: 100 },
                  { label: 'Has License', value: healthScore.has_license ? 100 : 0, max: 100 },
                  { label: 'Has Contributing Guide', value: healthScore.has_contributing ? 100 : 0, max: 100 },
                  { label: 'Has Screenshots', value: healthScore.has_screenshots ? 100 : 0, max: 100 },
                  { label: 'Has API Docs', value: healthScore.has_api_docs ? 100 : 0, max: 100 },
                  { label: 'Has Architecture Docs', value: healthScore.has_architecture ? 100 : 0, max: 100 },
                  { label: 'Has Examples', value: healthScore.has_examples ? 100 : 0, max: 100 },
                ].map((item, i) => (
                  <div key={i}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600 dark:text-gray-400">{item.label}</span>
                      <span className={item.value >= 50 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}>
                        {item.value}/{item.max}
                      </span>
                    </div>
                    <div className="w-full h-2 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${item.value >= 50 ? 'bg-green-500' : 'bg-red-500'}`}
                        style={{ width: `${(item.value / item.max) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {suggestions.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3">Improvement Suggestions</h3>
                  <ul className="space-y-2">
                    {suggestions.map((suggestion, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400">
                        <span className="text-brand-500 mt-0.5">→</span>
                        {suggestion}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {showPreview && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setShowPreview(false)}>
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-auto p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">README Preview</h3>
              <button onClick={() => setShowPreview(false)} className="text-gray-500 hover:text-gray-900 dark:hover:text-gray-100 text-2xl">&times;</button>
            </div>
            <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap font-mono">
              {readmeContent}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultCard;