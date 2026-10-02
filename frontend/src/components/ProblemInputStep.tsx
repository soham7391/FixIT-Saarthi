import React from 'react';
import { ArrowRight, AlertCircle, Terminal } from 'lucide-react';
import { useSystemMetrics, SystemMetricCard } from './SystemSnapshot';

interface ProblemInputStepProps {
  textInput: string;
  onChangeText: (text: string) => void;
  isLoading: boolean;
  error: string | null;
  onProceed: () => void;
}

const SAMPLE_PROMPTS = [
  'My PC freezes completely when playing games or running heavy software.',
  'Task Manager shows 100% CPU usage and Chrome process is not responding.',
  'System memory is stuck at 90% RAM usage and the laptop becomes sluggish.',
  'Disk usage remains at 100% and programs take ages to open.'
];

export const ProblemInputStep: React.FC<ProblemInputStepProps> = ({
  textInput,
  onChangeText,
  isLoading,
  error,
  onProceed
}) => {
  const { leftMetrics, rightMetrics } = useSystemMetrics();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-5 max-w-6xl mx-auto items-start transition-colors">
      {/* Left Column: System Environment Metrics */}
      <div className="md:col-span-1 lg:col-span-3 order-2 lg:order-1">
        <SystemMetricCard metrics={leftMetrics} title="System Environment" />
      </div>

      {/* Center Column: Primary Focus - Describe Your System Problem */}
      <div className="md:col-span-2 lg:col-span-6 order-1 lg:order-2 bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-6 shadow-md flex flex-col justify-between relative z-10">
        <div>
          {/* Header */}
          <div className="flex items-center gap-3 mb-5">
            <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-900/60 shadow-2xs">
              <Terminal className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900 dark:text-zinc-100">
                Describe Your System Problem
              </h2>
              <p className="text-xs text-slate-500 dark:text-zinc-400">
                Provide details about performance drops, freezing, or resource spikes.
              </p>
            </div>
          </div>

          {/* Text Input Area */}
          <div className="relative mb-4">
            <textarea
              value={textInput}
              onChange={(e) => onChangeText(e.target.value)}
              maxLength={1500}
              rows={4}
              placeholder="e.g., My computer slows down, Task Manager shows 100% CPU usage, and applications stop responding when multiple windows are open..."
              className="w-full bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 rounded-lg p-3.5 text-sm text-slate-900 dark:text-zinc-100 placeholder-slate-400 dark:placeholder-zinc-600 focus:outline-none focus:border-indigo-500 dark:focus:border-indigo-500 transition-all resize-none font-sans"
            />
            <div className="absolute right-3 bottom-3 text-[11px] text-slate-400 dark:text-zinc-500 font-mono">
              {textInput.length}/1500
            </div>
          </div>

          {/* Quick Starters */}
          <div className="mb-6">
            <p className="text-xs font-medium text-slate-500 dark:text-zinc-400 mb-2">
              Common Symptom Starters:
            </p>
            <div className="flex flex-wrap gap-2">
              {SAMPLE_PROMPTS.map((prompt, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => onChangeText(prompt)}
                  className="text-xs bg-slate-100 hover:bg-slate-200 dark:bg-zinc-800/80 dark:hover:bg-zinc-800 text-slate-700 dark:text-zinc-300 px-3 py-1.5 rounded-md border border-slate-200/80 dark:border-zinc-700/80 transition-all text-left"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* Out-of-domain / Scope Guard Error Alert */}
          {error && (
            <div className="mb-5 p-3.5 rounded-lg bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 flex items-start gap-3 text-xs text-rose-800 dark:text-rose-300">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600 dark:text-rose-400" />
              <div className="flex-1">
                <p className="font-semibold">{error}</p>
                <p className="text-[11px] text-rose-700/90 dark:text-rose-300/80 mt-0.5">
                  FixIT Saarthi supports computer troubleshooting for Performance & Freezing, Boot, and Network issues.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Action Controls */}
        <div className="flex justify-end pt-3 border-t border-slate-100 dark:border-zinc-800 mt-4">
          <button
            onClick={onProceed}
            disabled={isLoading}
            className="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-sm flex items-center justify-center gap-2 transition-all disabled:opacity-60"
          >
            {isLoading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Analyzing your problem...
              </>
            ) : (
              <>
                Continue to Diagnostic Questions
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>

      {/* Right Column: Hardware & Network Metrics */}
      <div className="md:col-span-1 lg:col-span-3 order-3 lg:order-3">
        <SystemMetricCard metrics={rightMetrics} title="Hardware & Network" />
      </div>
    </div>
  );
};
