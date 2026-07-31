import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GitHubIcon, SparklesIcon, ArrowRightIcon, CodeBracketIcon, DocumentTextIcon, BoltIcon } from '../components/icons';

const features = [
  {
    icon: <BoltIcon className="w-6 h-6" />,
    title: 'AI-Powered Analysis',
    description: 'Automatically analyze any GitHub repository and extract key insights about its tech stack, architecture, and dependencies.',
  },
  {
    icon: <DocumentTextIcon className="w-6 h-6" />,
    title: 'Professional README',
    description: 'Generate comprehensive, well-structured README documentation powered by Amazon Bedrock AI.',
  },
  {
    icon: <CodeBracketIcon className="w-6 h-6" />,
    title: 'Tech Stack Detection',
    description: 'Intelligently detect languages, frameworks, databases, deployment targets, and AI libraries from your codebase.',
  },
];

const LandingPage() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    navigate('/dashboard', { state: { repoUrl: url } });
  };

  return (
    <div className="min-h-screen flex flex-col">
      <section className="relative overflow-hidden bg-gradient-to-br from-brand-50 via-white to-brand-100 dark:from-gray-900 dark:via-gray-950 dark:to-gray-900">
        <div className="absolute inset-0 opacity-30 dark:opacity-10">
          <div className="absolute top-10 left-10 w-72 h-72 bg-brand-400 rounded-full blur-3xl" />
          <div className="absolute bottom-10 right-10 w-96 h-96 bg-brand-300 rounded-full blur-3xl" />
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
          <div className="text-center animate-fadeIn">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-100 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300 text-sm font-medium mb-8">
              <SparklesIcon className="w-4 h-4" />
              <span>Powered by Amazon Bedrock</span>
            </div>
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight mb-6">
              <span className="bg-gradient-to-r from-brand-600 to-brand-400 bg-clip-text text-transparent">
                RepoDoc AI
              </span>
            </h1>
            <p className="text-lg sm:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
              AI-powered documentation assistant. Paste a GitHub repository URL and get a complete, professional README in seconds.
            </p>
            <form onSubmit={handleSubmit} className="max-w-xl mx-auto mb-12">
              <div className="flex gap-3">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://github.com/user/repo"
                  className="input-field flex-1 text-base"
                  required
                />
                <button type="submit" disabled={loading} className="btn-primary text-base px-8">
                  {loading ? 'Analyzing...' : 'Analyze'}
                </button>
              </div>
            </form>
            <p className="text-sm text-gray-500 dark:text-gray-500">
              Supports public repositories. No code is stored — analysis happens in real-time.
            </p>
          </div>
        </div>
      </section>

      <section className="py-20 md:py-28">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Everything you need for great docs</h2>
            <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              RepoDoc AI goes beyond a simple README generator. It analyzes your entire codebase and produces comprehensive documentation.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="card p-8 animate-slideUp"
                style={{ animationDelay: `${index * 0.15}s` }}
              >
                <div className="w-12 h-12 rounded-xl bg-brand-100 dark:bg-brand-900/30 text-brand-600 dark:text-brand-400 flex items-center justify-center mb-5">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 md:py-28 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { value: '10K+', label: 'Repositories Analyzed' },
              { value: '98%', label: 'Documentation Quality' },
              { value: '< 30s', label: 'Analysis Time' },
              { value: 'AI-Powered', label: 'Bedrock Integration' },
            ].map((stat, index) => (
              <div key={index}>
                <div className="text-3xl sm:text-4xl font-extrabold text-brand-600 dark:text-brand-400 mb-1">{stat.value}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

export default LandingPage;