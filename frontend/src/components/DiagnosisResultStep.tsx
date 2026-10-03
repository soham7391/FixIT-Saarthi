import React from 'react';
import { ArrowLeft, ChevronRight, Activity, Terminal } from 'lucide-react';
import type { RankedCause, Observation } from '../types/diagnostic';

interface DiagnosisResultStepProps {
  rankedCauses: RankedCause[];
  observations: Observation[];
  onSelectCause: (cause: RankedCause) => void;
  onBackToInputs: () => void;
}

export const DiagnosisResultStep: React.FC<DiagnosisResultStepProps> = ({
  rankedCauses,
  observations,
  onSelectCause,
  onBackToInputs
}) => {
  return (
    <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-6 shadow-sm max-w-4xl mx-auto transition-colors">
      {/* Header */}
      <div className="flex items-center justify-between mb-5 pb-4 border-b border-slate-100 dark:border-zinc-800">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 border border-slate-200 dark:border-zinc-700">
            <Terminal className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-slate-900 dark:text-zinc-100">
              Expert Engine Diagnostic Results
            </h2>
            <p className="text-xs text-slate-500 dark:text-zinc-400">
              Deterministic rule evaluation based on active observations.
            </p>
          </div>
        </div>

        <button
          onClick={onBackToInputs}
          className="text-xs text-slate-600 dark:text-zinc-300 hover:text-slate-900 dark:hover:text-white flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-slate-100 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Refine Observations
        </button>
      </div>

      {/* Evaluated Observations Summary */}
      {observations.length > 0 && (
        <div className="mb-6 p-3.5 rounded-lg bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800">
          <div className="flex items-center gap-2 mb-2 text-xs font-medium text-slate-600 dark:text-zinc-400">
            <Activity className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
            Evaluated Symptom Observations ({observations.length}):
          </div>
          <div className="flex flex-wrap gap-2">
            {observations.map((obs, i) => (
              <span
                key={i}
                className="px-2.5 py-1 rounded text-[11px] font-mono bg-white dark:bg-zinc-900 text-slate-700 dark:text-zinc-300 border border-slate-200 dark:border-zinc-800 shadow-2xs"
              >
                {obs.key}: <span className="text-indigo-600 dark:text-indigo-400 font-semibold">{String(obs.value)}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Ranked Causes List */}
      <div className="space-y-4 mb-6">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
          Ranked Potential Causes ({rankedCauses.length})
        </h3>

        {rankedCauses.length === 0 ? (
          <div className="p-8 text-center bg-slate-50 dark:bg-zinc-950 rounded-lg border border-slate-200 dark:border-zinc-800 text-slate-500 dark:text-zinc-400 text-xs">
            No matching causes identified. Try adding more problem details or answering diagnostic questions.
          </div>
        ) : (
          rankedCauses.map((cause, idx) => {
            const confidencePct = Math.round(cause.confidence_score * 100);
            const isTopMatch = idx === 0;

            return (
              <div
                key={cause.cause_id}
                className={`p-5 rounded-lg border transition-all ${
                  isTopMatch
                    ? 'bg-slate-50/80 dark:bg-zinc-950/80 border-indigo-200 dark:border-zinc-700 shadow-xs'
                    : 'bg-white dark:bg-zinc-950/40 border-slate-200 dark:border-zinc-800 hover:border-slate-300 dark:hover:border-zinc-700'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
                  <div className="flex items-center gap-2.5">
                    {isTopMatch && (
                      <span className="px-2 py-0.5 rounded bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 text-[10px] font-semibold uppercase tracking-wider">
                        Primary Cause
                      </span>
                    )}
                    <h4 className="text-base font-semibold text-slate-900 dark:text-zinc-100">{cause.cause_name}</h4>
                  </div>

                  {/* Confidence Bar */}
                  <div className="flex items-center gap-3">
                    <div className="w-24 bg-slate-200 dark:bg-zinc-800 h-1.5 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          confidencePct >= 80
                            ? 'bg-indigo-600 dark:bg-indigo-400'
                            : confidencePct >= 50
                            ? 'bg-amber-500'
                            : 'bg-slate-400'
                        }`}
                        style={{ width: `${confidencePct}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono font-semibold text-slate-700 dark:text-zinc-300">
                      {confidencePct}% Confidence
                    </span>
                  </div>
                </div>

                {/* Reasoning Explanation */}
                <div className="p-3 rounded bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 mb-3 text-xs text-slate-700 dark:text-zinc-300 leading-relaxed">
                  <span className="font-semibold text-slate-500 dark:text-zinc-400 block mb-1">
                    Rule Evaluation Analysis:
                  </span>
                  {cause.reasoning}
                </div>

                {/* Matched Symptoms */}
                {cause.matched_symptoms.length > 0 && (
                  <div className="flex flex-wrap items-center gap-1.5 mb-4">
                    <span className="text-[11px] text-slate-500 dark:text-zinc-500 font-medium mr-1">Trigger Rules:</span>
                    {cause.matched_symptoms.map((symptom, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400 border border-slate-200 dark:border-zinc-700"
                      >
                        {symptom}
                      </span>
                    ))}
                  </div>
                )}

                {/* Action Button */}
                <div className="flex justify-end">
                  <button
                    onClick={() => onSelectCause(cause)}
                    className={`px-4 py-2 rounded-md text-xs font-medium flex items-center gap-2 transition-all ${
                      isTopMatch
                        ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm'
                        : 'bg-slate-100 dark:bg-zinc-800 hover:bg-slate-200 dark:hover:bg-zinc-700 text-slate-700 dark:text-zinc-200 border border-slate-200 dark:border-zinc-700'
                    }`}
                  >
                    View Troubleshooting Steps ({cause.fix_steps.length})
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
