import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GitHubIcon, SparklesIcon, ArrowRightIcon, CodeBracketIcon, DocumentTextIcon, BoltIcon, CheckCircleIcon, ServerIcon, DatabaseIcon, RocketIcon, ShieldCheckIcon } from '../components/icons';
import { validateGitHubUrl } from '../utils/validation';

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

const stats = [
  { value: '10K+', label: 'Repositories Analyzed' },
  { value: '98%', label: 'Documentation Quality' },
  { value: '< 30s', label: 'Analysis Time' },
  { value: 'AI-Powered', label: 'Bedrock Integration' },
];

const howItWorks = [
  {
    step: '01',
    title: 'Paste Repository URL',
    description: 'Simply paste any public GitHub repository URL into the input field.',
    icon: <GitHubIcon className="w-8 h-8" />,
  },
  {
    step: '02',
    title: 'AI Analyzes Your Code',
    description: 'Our engine fetches the repository, detects the tech stack, and analyzes the codebase structure.',
    icon: <BoltIcon className="w-8 h-8" />,
  },
  {
    step: '03',
    title: 'Download Documentation',
    description: 'Get a complete, professional README with installation guide, API docs, and improvement suggestions.',
    icon: <DocumentTextIcon className="w-8 h-8" />,
  },
];

const ScrollReveal = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => {
  const ref = React.useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = React.useState(false);

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={`transition-all duration-700 ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
      } ${className}`}
    >
      {children}
    </div>
  );
};

const LandingPage = () => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const validation = validateGitHubUrl(url);
    if (!validation.valid) {
      setError(validation.error || 'Invalid URL');
      return;
    }

    setLoading(true);
    navigate('/dashboard', { state: { repoUrl: url } });
  };

  return (
    <div className="min-h-screen flex flex-col">
      <section className="relative overflow-hidden bg-gradient-to-br from-brand-50 via-white to-brand-100 dark:from-gray-900 dark:via-gray-950 dark:to-gray-900">
        <div className="absolute inset-0 opacity-30 dark:opacity-10">
          <div className="absolute top-10 left-10 w-72 h-72 bg-brand-400 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-10 right-10 w-96 h-96 bg-brand-300 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
          <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-brand-200 dark:bg-brand-800 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
          <ScrollReveal>
            <div className="text-center">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-100 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300 text-sm font-medium mb-8 animate-fadeIn">
                <SparklesIcon className="w-4 h-4" />
                <span>Powered by Amazon Bedrock</span>
              </div>
              <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight mb-6 animate-slideUp">
                <span className="bg-gradient-to-r from-brand-600 to-brand-400 bg-clip-text text-transparent">
                  RepoDoc AI
                </span>
              </h1>
              <p className="text-lg sm:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed animate-slideUp" style={{ animationDelay: '0.1s' }}>
                AI-powered documentation assistant. Paste a GitHub repository URL and get a complete, professional README in seconds.
              </p>
              <form onSubmit={handleSubmit} className="max-w-xl mx-auto mb-12 animate-slideUp" style={{ animationDelay: '0.2s' }}>
                <div className="flex gap-3">
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => {
                      setUrl(e.target.value);
                      setError('');
                    }}
                    placeholder="https://github.com/user/repo"
                    className={`input-field flex-1 text-base ${error ? 'border-red-500 focus:ring-red-500' : ''}`}
                    required
                  />
                  <button type="submit" disabled={loading} className="btn-primary text-base px-8">
                    {loading ? 'Analyzing...' : 'Analyze'}
                  </button>
                </div>
                {error && (
                  <p className="text-red-500 dark:text-red-400 text-sm mt-2 animate-fadeIn">{error}</p>
                )}
              </form>
              <p className="text-sm text-gray-500 dark:text-gray-500 animate-slideUp" style={{ animationDelay: '0.3s' }}>
                Supports public repositories. No code is stored — analysis happens in real-time.
              </p>
            </div>
          </ScrollReveal>
        </div>
      </section>

      <section className="py-20 md:py-28">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">Everything you need for great docs</h2>
              <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                RepoDoc AI goes beyond a simple README generator. It analyzes your entire codebase and produces comprehensive documentation.
              </p>
            </div>
          </ScrollReveal>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <ScrollReveal key={index}>
                <div
                  className="card p-8 group hover:scale-[1.02] transition-transform duration-300"
                  style={{ animationDelay: `${index * 0.15}s` }}
                >
                  <div className="w-12 h-12 rounded-xl bg-brand-100 dark:bg-brand-900/30 text-brand-600 dark:text-brand-400 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                  <p className="text-gray-600 dark:text-gray-400 leading-relaxed">{feature.description}</p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 md:py-28 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">How it works</h2>
              <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                Three simple steps to generate professional documentation for any GitHub repository.
              </p>
            </div>
          </ScrollReveal>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {howItWorks.map((step, index) => (
              <ScrollReveal key={index}>
                <div className="card p-8 text-center group hover:scale-[1.02] transition-transform duration-300">
                  <div className="w-16 h-16 rounded-2xl bg-brand-100 dark:bg-brand-900/30 text-brand-600 dark:text-brand-400 flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                    {step.icon}
                  </div>
                  <div className="text-sm font-bold text-brand-500 dark:text-brand-400 mb-2">{step.step}</div>
                  <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
                  <p className="text-gray-600 dark:text-gray-400 leading-relaxed">{step.description}</p>
                </div>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 md:py-28">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ScrollReveal>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
              {stats.map((stat, index) => (
                <div key={index} className="animate-slideUp" style={{ animationDelay: `${index * 0.1}s` }}>
                  <div className="text-3xl sm:text-4xl font-extrabold text-brand-600 dark:text-brand-400 mb-1">{stat.value}</div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</div>
                </div>
              ))}
            </div>
          </ScrollReveal>
        </div>
      </section>

      <section className="py-20 md:py-28 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <ScrollReveal>
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Ready to document your project?</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-8">
              Stop wasting time on documentation. Let AI handle it so you can focus on building great products.
            </p>
            <button
              onClick={() => navigate('/')}
              className="btn-primary text-lg px-8 py-4 inline-flex items-center gap-2"
            >
              Get Started Free
              <ArrowRightIcon className="w-5 h-5" />
            </button>
          </ScrollReveal>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;