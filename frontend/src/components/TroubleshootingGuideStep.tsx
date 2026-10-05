import React, { useState } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  Wrench,
  CheckCircle2,
  ArrowLeft,
  RefreshCw,
  Check,
  RotateCcw,
  HelpCircle,
  FileText
} from 'lucide-react';
import { SafetyLevel } from '../types/diagnostic';
import type { RankedCause } from '../types/diagnostic';

interface TroubleshootingGuideStepProps {
  cause: RankedCause;
  allCauses: RankedCause[];
  onSelectOtherCause: (cause: RankedCause) => void;
  onBackToDiagnosis: () => void;
  onResetSession: () => void;
  onConfirmResolved?: (completedSteps: Record<number, boolean>) => void;
  onOpenReport?: (completedSteps: Record<number, boolean>) => void;
  isResolvedInitial?: boolean;
}

export const TroubleshootingGuideStep: React.FC<TroubleshootingGuideStepProps> = ({
  cause,
  allCauses,
  onSelectOtherCause,
  onBackToDiagnosis,
  onResetSession,
  onConfirmResolved,
  onOpenReport,
  isResolvedInitial = false
}) => {
  const [completedSteps, setCompletedSteps] = useState<Record<number, boolean>>({});
  const [isConfirmedResolved, setIsConfirmedResolved] = useState<boolean>(isResolvedInitial);

  const toggleStep = (stepNum: number) => {
    setCompletedSteps((prev) => ({ ...prev, [stepNum]: !prev[stepNum] }));
  };

  const handleResolve = () => {
    setIsConfirmedResolved(true);
    onConfirmResolved?.(completedSteps);
  };

  const getSafetyBadge = (level: SafetyLevel) => {
    switch (level) {
      case SafetyLevel.SAFE:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 text-[11px] font-medium">
            <ShieldCheck className="w-3.5 h-3.5" />
            Safe (No System Risk)
          </span>
        );
      case SafetyLevel.CAUTION:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-800 text-[11px] font-medium">
            <AlertTriangle className="w-3.5 h-3.5" />
            Caution (Save Work First)
          </span>
        );
      case SafetyLevel.ADVANCED:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-800 text-[11px] font-medium">
            <Wrench className="w-3.5 h-3.5" />
            Advanced (Admin Privileges)
          </span>
        );
      default:
        return null;
    }
  };

  const currentCauseIndex = allCauses.findIndex((c) => c.cause_id === cause.cause_id);
  const nextCause = currentCauseIndex >= 0 && currentCauseIndex < allCauses.length - 1 ? allCauses[currentCauseIndex + 1] : null;

  return (
    <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-6 shadow-sm max-w-4xl mx-auto transition-colors">
      {/* Top Controls */}
      <div className="flex items-center justify-between mb-5 pb-4 border-b border-slate-100 dark:border-zinc-800">
        <button
          onClick={onBackToDiagnosis}
          className="text-xs text-slate-600 dark:text-zinc-300 hover:text-slate-900 dark:hover:text-white flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-slate-100 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to All Causes
        </button>

        <div className="flex items-center gap-2">
          {allCauses.length > 1 && (
            <span className="text-xs text-slate-500 dark:text-zinc-400 font-mono">
              Cause {currentCauseIndex + 1} of {allCauses.length}
            </span>
          )}
        </div>
      </div>

      {/* Cause Summary Banner */}
      <div className="p-5 rounded-lg bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-2">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-zinc-100">{cause.cause_name}</h2>
          <span className="px-2.5 py-0.5 rounded bg-slate-200 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 text-xs font-mono font-semibold">
            {Math.round(cause.confidence_score * 100)}% Confidence Match
          </span>
        </div>
        <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed mb-3">{cause.reasoning}</p>

        {cause.matched_symptoms.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            <span className="text-[11px] text-slate-500 dark:text-zinc-500 font-medium">Triggered by:</span>
            {cause.matched_symptoms.map((s, i) => (
              <span key={i} className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-200 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 border border-slate-300 dark:border-zinc-700">
                {s}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Confirmed Resolved Banner (ONLY shown AFTER explicit user confirmation) */}
      {isConfirmedResolved ? (
        <div className="p-6 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-center mb-6">
          <div className="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-900/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto mb-3">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <h3 className="text-base font-semibold text-emerald-900 dark:text-emerald-200 mb-1">
            Troubleshooting Confirmed Resolved
          </h3>
          <p className="text-xs text-emerald-700 dark:text-emerald-300/80 mb-4 max-w-md mx-auto">
            Session updated. Thank you for confirming that the recommended fix steps resolved your system issue.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            <button
              onClick={() => onOpenReport?.(completedSteps)}
              className="px-4 py-2 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-sm flex items-center gap-2 transition-all"
            >
              <FileText className="w-3.5 h-3.5" />
              Generate Diagnosis Report
            </button>
            <button
              onClick={onResetSession}
              className="px-4 py-2 rounded-md bg-slate-200 dark:bg-zinc-800 hover:bg-slate-300 dark:hover:bg-zinc-700 text-slate-700 dark:text-zinc-300 text-xs font-medium transition-all flex items-center gap-2"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Start New Session
            </button>
          </div>
        </div>
      ) : (
        /* Step-by-Step Fix Action Cards */
        <div className="space-y-4 mb-8">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400 flex items-center justify-between">
            <span>Step-by-Step Fix Actions ({cause.fix_steps.length})</span>
            <span className="text-[11px] font-normal text-slate-400 dark:text-zinc-500">Check steps as completed</span>
          </h3>

          {cause.fix_steps.map((step) => {
            const isDone = Boolean(completedSteps[step.step_number]);

            return (
              <div
                key={step.step_number}
                className={`p-5 rounded-lg border transition-all ${
                  isDone
                    ? 'bg-slate-50/50 dark:bg-zinc-950/40 border-slate-200 dark:border-zinc-800/60 opacity-75'
                    : 'bg-white dark:bg-zinc-950 border-slate-200 dark:border-zinc-800'
                }`}
              >
                <div className="flex items-start gap-3.5">
                  {/* Step Checkbox */}
                  <button
                    onClick={() => toggleStep(step.step_number)}
                    className={`w-5 h-5 rounded flex items-center justify-center border shrink-0 mt-0.5 transition-all ${
                      isDone
                        ? 'bg-emerald-600 border-emerald-600 text-white'
                        : 'bg-slate-50 dark:bg-zinc-900 border-slate-300 dark:border-zinc-700 text-transparent'
                    }`}
                  >
                    <Check className="w-3.5 h-3.5 stroke-[2.5]" />
                  </button>

                  <div className="flex-1">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 border border-slate-200 dark:border-zinc-700">
                          Step {step.step_number}
                        </span>
                        <h4 className={`text-sm font-semibold ${isDone ? 'line-through text-slate-400 dark:text-zinc-500' : 'text-slate-900 dark:text-zinc-100'}`}>
                          {step.title}
                        </h4>
                      </div>

                      {getSafetyBadge(step.safety_level)}
                    </div>

                    {/* Instruction */}
                    <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed mb-3">{step.instruction}</p>

                    {/* Warning Note */}
                    {step.warning_note && (
                      <div className="p-3 rounded bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/60 text-amber-800 dark:text-amber-300 text-xs mb-3 flex items-start gap-2">
                        <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                        <div>
                          <span className="font-semibold block">Important Warning:</span>
                          {step.warning_note}
                        </div>
                      </div>
                    )}

                    {/* Verification Question */}
                    <div className="p-2.5 rounded bg-slate-50 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-xs text-slate-600 dark:text-zinc-400">
                      <span className="font-semibold text-slate-700 dark:text-zinc-300 block mb-0.5">Verification Check:</span>
                      {step.verification_question}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Verification Prompt (BEFORE user confirmation) */}
      {!isConfirmedResolved && (
        <div className="p-5 rounded-lg bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-3 flex items-center gap-2">
            <HelpCircle className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            Did this fix your problem?
          </h4>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleResolve}
              className="px-4 py-2 rounded-md bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium flex items-center gap-2 shadow-sm transition-all"
            >
              <CheckCircle2 className="w-4 h-4" />
              Yes, Problem Resolved
            </button>

            {nextCause && (
              <button
                onClick={() => onSelectOtherCause(nextCause)}
                className="px-4 py-2 rounded-md bg-slate-100 dark:bg-zinc-800 hover:bg-slate-200 dark:hover:bg-zinc-700 text-slate-700 dark:text-zinc-200 text-xs font-medium border border-slate-200 dark:border-zinc-700 transition-all flex items-center gap-1.5"
              >
                <RotateCcw className="w-3.5 h-3.5 text-amber-500" />
                Not yet / Try Next Cause ({nextCause.cause_name})
              </button>
            )}

            <button
              onClick={onBackToDiagnosis}
              className="px-4 py-2 rounded-md bg-slate-100 dark:bg-zinc-800 hover:bg-slate-200 dark:hover:bg-zinc-700 text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white text-xs font-medium border border-slate-200 dark:border-zinc-700 transition-all"
            >
              Continue / Refine Diagnosis
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
