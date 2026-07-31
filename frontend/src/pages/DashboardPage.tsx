import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AnalysisResult, AnalysisStatus } from '../types';
import { analyzeRepository } from '../services/api';
import Header from '../components/Header';
import LoadingState from '../components/LoadingState';
import ResultCard from '../components/ResultCard';
import ErrorState from '../components/ErrorState';

const DashboardPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [status, setStatus] = useState<AnalysisStatus>({
    status: 'idle',
    progress: 0,
    message: '',
  });
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const repoUrl = location.state?.repoUrl as string | undefined;
    if (!repoUrl) {
      navigate('/');
      return;
    }
    runAnalysis(repoUrl);
  }, [location.state, navigate]);

  const runAnalysis = async (repoUrl: string) => {
    setStatus({ status: 'analyzing', progress: 0, message: 'Fetching repository metadata...' });
    setError(null);

    try {
      const response = await analyzeRepository(repoUrl);
      setStatus({ status: 'complete', progress: 100, message: 'Analysis complete!' });
      setResult(response.data);
    } catch (err) {
      setStatus({ status: 'error', progress: 0, message: 'Analysis failed' });
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    }
  };

  const handleNewAnalysis = () => {
    setResult(null);
    setError(null);
    setStatus({ status: 'idle', progress: 0, message: '' });
    navigate('/');
  };

  return (
    <div className="min-h-screen flex flex-col bg-white dark:bg-gray-950">
      <Header />
      <main className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-12">
        {status.status === 'idle' && (
          <div className="text-center py-20">
            <p className="text-gray-500 dark:text-gray-400">Redirecting to home...</p>
          </div>
        )}

        {status.status === 'analyzing' && (
          <LoadingState
            progress={status.progress}
            message={status.message}
          />
        )}

        {status.status === 'error' && error && (
          <ErrorState message={error} onRetry={handleNewAnalysis} />
        )}

        {status.status === 'complete' && result && (
          <div className="space-y-8 animate-fadeIn">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold">Analysis Complete</h1>
              <button onClick={handleNewAnalysis} className="btn-secondary text-sm">
                New Analysis
              </button>
            </div>

            <ResultCard
              repository={result.repository}
              techStack={result.tech_stack}
              folderStructure={result.folder_structure}
              architectureSummary={result.architecture_summary}
              readmeContent={result.readme_content}
              installationGuide={result.installation_guide}
              apiDocumentation={result.api_documentation}
              healthScore={result.health_score}
              suggestions={result.suggestions}
            />
          </div>
        )}
      </main>
    </div>
  );
}

export default DashboardPage;