interface LoadingStateProps {
  progress: number;
  message: string;
}

const LoadingState = ({ progress, message }: LoadingStateProps) => {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="relative w-16 h-16 mb-6">
        <div className="absolute inset-0 rounded-full border-4 border-brand-100 dark:border-brand-900/30" />
        <div
          className="absolute inset-0 rounded-full border-4 border-transparent border-t-brand-600 animate-spin"
          style={{ animationDuration: '1s' }}
        />
        <div className="absolute inset-2 rounded-full border-4 border-transparent border-t-brand-400 animate-spin" style={{ animationDuration: '0.6s', animationDirection: 'reverse' }} />
      </div>
      <h2 className="text-xl font-semibold mb-2">Analyzing Repository</h2>
      <p className="text-gray-500 dark:text-gray-400 mb-6">{message}</p>
      <div className="w-64 h-2 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-brand-600 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className="text-sm text-gray-400 dark:text-gray-600 mt-3">{progress}%</p>
    </div>
  );
};

export default LoadingState;