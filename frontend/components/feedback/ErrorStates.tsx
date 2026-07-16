import { AlertCircle, WifiOff, ShieldAlert, Clock, FileWarning } from "lucide-react";
import React from "react";

interface ErrorProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

function BaseError({ icon: Icon, title, message, onRetry, colorClass }: ErrorProps & { icon: React.ElementType, colorClass: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-100 dark:border-gray-800">
      <div className={`p-3 rounded-full mb-4 ${colorClass}`}>
        <Icon className="w-8 h-8" />
      </div>
      <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">{title}</h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 max-w-md mb-6">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md shadow-sm transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
}

export function NetworkError({ onRetry, title = "Connection Lost", message = "We couldn't connect to the server. Please check your internet connection and try again." }: ErrorProps) {
  return <BaseError icon={WifiOff} title={title} message={message} onRetry={onRetry} colorClass="bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400" />;
}

export function PermissionError({ onRetry, title = "Access Denied", message = "You don't have permission to view this resource. Contact your administrator if you believe this is a mistake." }: ErrorProps) {
  return <BaseError icon={ShieldAlert} title={title} message={message} onRetry={onRetry} colorClass="bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400" />;
}

export function TimeoutError({ onRetry, title = "Request Timed Out", message = "The server took too long to respond. This might be a temporary issue." }: ErrorProps) {
  return <BaseError icon={Clock} title={title} message={message} onRetry={onRetry} colorClass="bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400" />;
}

export function OfflineError({ onRetry, title = "You are Offline", message = "It looks like you've lost your internet connection. We'll automatically reconnect when you're back online." }: ErrorProps) {
  return <BaseError icon={WifiOff} title={title} message={message} onRetry={onRetry} colorClass="bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400" />;
}

export function ValidationError({ onRetry, title = "Invalid Request", message = "The information provided was invalid. Please check your inputs and try again." }: ErrorProps) {
  return <BaseError icon={FileWarning} title={title} message={message} onRetry={onRetry} colorClass="bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400" />;
}

export function UnexpectedError({ onRetry, title = "Unexpected Error", message = "Something went wrong on our end. Our team has been notified." }: ErrorProps) {
  return <BaseError icon={AlertCircle} title={title} message={message} onRetry={onRetry} colorClass="bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400" />;
}
