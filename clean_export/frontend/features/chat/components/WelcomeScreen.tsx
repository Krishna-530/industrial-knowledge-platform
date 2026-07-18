import React from "react";
import { MessageSquarePlus } from "lucide-react";

interface WelcomeScreenProps {
  onStartConversation: () => void;
}

export function WelcomeScreen({ onStartConversation }: WelcomeScreenProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-white dark:bg-gray-900 h-full w-full">
      <div className="w-20 h-20 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-3xl flex items-center justify-center mb-6 shadow-sm ring-1 ring-blue-100 dark:ring-blue-900/50">
        <MessageSquarePlus className="w-10 h-10" />
      </div>
      
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4 tracking-tight">
        How can I help you today?
      </h1>
      
      <p className="text-lg text-gray-500 dark:text-gray-400 max-w-lg mb-8">
        Access technical specifications, maintenance records, standard operating procedures, and real-time equipment diagnostics across your entire industrial knowledge base.
      </p>
      
      <button
        onClick={onStartConversation}
        className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
      >
        Start a new conversation
      </button>

      <div className="mt-12 grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl w-full">
        {/* Suggestion Chips */}
        <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800 text-sm text-left text-gray-600 dark:text-gray-300">
          <span className="font-semibold block mb-1">Diagnose Equipment</span>
          "Why did Pump A-124 report a vibration alert yesterday?"
        </div>
        <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800 text-sm text-left text-gray-600 dark:text-gray-300">
          <span className="font-semibold block mb-1">Find Procedures</span>
          "Show me the standard operating procedure for turbine shutdown."
        </div>
      </div>
    </div>
  );
}
