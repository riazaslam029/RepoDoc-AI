import { XCircleIcon, RefreshIcon } from './icons';

interface ErrorStateProps {
  message: string;
  onRetry: () => void;
}

const ErrorState = ({ message, onRetry }: ErrorStateProps) => {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mb-6">
        <XCircleIcon className="w-8 h-8 text-red-500" />
      </div>
      <h2 className="text-xl font-semibold mb-2">Analysis Failed</h2>
      <p className="text-gray-500 dark:text-gray-400 mb-6 text-center max-w-md">{message}</p>
      <button onClick={onRetry} className="btn-primary flex items-center gap-2">
        <RefreshIcon className="w-4 h-4" />
        Try Again
      </button>
    </div>
  );
};

export default ErrorState;