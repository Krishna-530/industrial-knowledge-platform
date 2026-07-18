export default function ErrorState({ error, onRetry }: { error: Error | string, onRetry?: () => void }) {
  const message = typeof error === "string" ? error : error.message;
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-danger/10 border border-danger/20 rounded-xl">
      <h3 className="text-lg font-semibold text-danger mb-2">An error occurred</h3>
      <p className="text-danger/80 text-sm max-w-md mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-danger text-white rounded-md text-sm font-medium hover:bg-danger/90"
        >
          Retry
        </button>
      )}
    </div>
  );
}
