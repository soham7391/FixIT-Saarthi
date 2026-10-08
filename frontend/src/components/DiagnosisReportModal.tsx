import React from 'react';
import { X, Printer, CheckCircle2, ShieldCheck, Laptop, Globe, Cpu, HardDrive, Monitor, Wifi, FileText } from 'lucide-react';
import { DomainEnum } from '../types/diagnostic';
import type { Observation, RankedCause } from '../types/diagnostic';
import { useSystemMetrics } from './SystemSnapshot';

interface DiagnosisReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId: string | null;
  domain: DomainEnum;
  problemDescription: string;
  answers: Record<string, boolean | undefined>;
  processedObservations: Observation[];
  rankedCauses: RankedCause[];
  selectedCause: RankedCause | null;
  completedSteps: Record<number, boolean>;
  resolvedAt: string;
}

export const DiagnosisReportModal: React.FC<DiagnosisReportModalProps> = ({
  isOpen,
  onClose,
  sessionId,
  domain,
  problemDescription,
  answers,
  processedObservations,
  rankedCauses,
  selectedCause,
  completedSteps,
  resolvedAt
}) => {
  const { leftMetrics, rightMetrics } = useSystemMetrics();

  if (!isOpen) return null;

  const DOMAIN_LABELS: Record<DomainEnum, string> = {
    [DomainEnum.PERFORMANCE]: 'Performance & Freezing',
    [DomainEnum.BOOT_FAILURE]: 'Boot Failure & Startup',
    [DomainEnum.NETWORK]: 'Network & Connectivity',
    [DomainEnum.DRIVER_PERIPHERAL]: 'Driver & Peripherals'
  };

  const answeredList = Object.entries(answers).filter(([_, val]) => val !== undefined);
  const yesAnswers = answeredList.filter(([_, val]) => val === true);
  const noAnswers = answeredList.filter(([_, val]) => val === false);
  const skippedCount = Object.keys(answers).filter((k) => answers[k] === undefined).length;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs overflow-y-auto printable-report-modal">
      <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] flex flex-col overflow-hidden transition-all printable-report-card">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-zinc-800 flex items-center justify-between bg-slate-50 dark:bg-zinc-950">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-zinc-100">
                FixIT Saarthi — Resolved Diagnosis Report
              </h2>
              <p className="text-xs text-slate-500 dark:text-zinc-400">
                Official troubleshooting session summary & verification record
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 print:hidden">
            <button
              onClick={handlePrint}
              className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium flex items-center gap-1.5 shadow-sm transition-all"
              title="Print or Save as PDF"
            >
              <Printer className="w-3.5 h-3.5" />
              Print / Save PDF
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-zinc-200 hover:bg-slate-200 dark:hover:bg-zinc-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-800 dark:text-zinc-200 printable-report-content">
          {/* Section 1: Session Overview Banner */}
          <div className="p-4 rounded-xl bg-emerald-50/70 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900/60 flex flex-col sm:flex-row sm:items-center justify-between gap-4 print-break-inside-avoid">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2 py-0.5 rounded bg-emerald-600 text-white font-mono font-semibold text-[10px] uppercase">
                  Status: Resolved
                </span>
                <span className="font-mono text-slate-500 dark:text-zinc-400 text-[11px]">
                  ID: {sessionId || 'N/A'}
                </span>
              </div>
              <p className="text-xs font-semibold text-emerald-900 dark:text-emerald-200">
                Domain: {DOMAIN_LABELS[domain] || domain}
              </p>
              <p className="text-[11px] text-emerald-700/80 dark:text-emerald-300/70">
                Confirmed resolved at: {new Date(resolvedAt).toLocaleString()}
              </p>
            </div>
          </div>

          {/* Section 2: System Environment Snapshot */}
          <div className="border border-slate-200 dark:border-zinc-800 rounded-xl p-4 bg-slate-50/50 dark:bg-zinc-950/40 print-break-inside-avoid">
            <h3 className="font-bold text-slate-900 dark:text-zinc-100 mb-3 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
              <Laptop className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              Device & System Environment Snapshot
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {[...leftMetrics, ...rightMetrics].map((m, i) => (
                <div key={i} className="p-2.5 rounded-lg bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800">
                  <span className="text-[10px] text-slate-400 dark:text-zinc-500 block mb-0.5">{m.label}</span>
                  <span className="font-medium text-slate-800 dark:text-zinc-200 text-xs">{m.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Section 3: Problem Description */}
          <div className="border border-slate-200 dark:border-zinc-800 rounded-xl p-4 bg-white dark:bg-zinc-900 print-break-inside-avoid">
            <h3 className="font-bold text-slate-900 dark:text-zinc-100 mb-2 uppercase tracking-wider text-[11px]">
              Original Problem Description
            </h3>
            <p className="p-3 rounded-lg bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 font-sans text-slate-700 dark:text-zinc-300 leading-relaxed italic">
              "{problemDescription || 'No initial text problem provided.'}"
            </p>
          </div>

          {/* Section 4: Diagnostic Interaction & Observations */}
          <div className="border border-slate-200 dark:border-zinc-800 rounded-xl p-4 bg-white dark:bg-zinc-900 print-break-inside-avoid">
            <h3 className="font-bold text-slate-900 dark:text-zinc-100 mb-3 uppercase tracking-wider text-[11px]">
              Questionnaire Answers & Engine Observations
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-3">
              <div className="p-3 rounded-lg bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800">
                <span className="font-semibold text-slate-700 dark:text-zinc-300 block mb-1">Affirmative Symptoms (Yes):</span>
                {yesAnswers.length > 0 ? (
                  <ul className="list-disc list-inside space-y-1 text-emerald-700 dark:text-emerald-400 font-mono text-[11px]">
                    {yesAnswers.map(([k]) => (
                      <li key={k}>{k}</li>
                    ))}
                  </ul>
                ) : (
                  <span className="text-slate-400 dark:text-zinc-500 italic">None selected</span>
                )}
              </div>

              <div className="p-3 rounded-lg bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800">
                <span className="font-semibold text-slate-700 dark:text-zinc-300 block mb-1">Negative Symptoms (No):</span>
                {noAnswers.length > 0 ? (
                  <ul className="list-disc list-inside space-y-1 text-slate-500 dark:text-zinc-400 font-mono text-[11px]">
                    {noAnswers.map(([k]) => (
                      <li key={k}>{k}</li>
                    ))}
                  </ul>
                ) : (
                  <span className="text-slate-400 dark:text-zinc-500 italic">None selected</span>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-zinc-400 pt-2 border-t border-slate-100 dark:border-zinc-800 font-mono">
              <span>Skipped Questions: {skippedCount}</span>
              <span>Total Engine Observations Evaluated: {processedObservations.length}</span>
            </div>
          </div>

          {/* Section 5: Evaluated Diagnosis & Ranked Causes */}
          <div className="border border-slate-200 dark:border-zinc-800 rounded-xl p-4 bg-white dark:bg-zinc-900 print-break-inside-avoid">
            <h3 className="font-bold text-slate-900 dark:text-zinc-100 mb-3 uppercase tracking-wider text-[11px]">
              Expert Engine Diagnostic Candidate Ranking
            </h3>

            {selectedCause && (
              <div className="p-3.5 rounded-lg bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-900/60 mb-3">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="font-bold text-indigo-900 dark:text-indigo-200 text-xs">
                    Primary Cause: {selectedCause.cause_name}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-indigo-600 text-white font-mono font-semibold text-[10px]">
                    {Math.round(selectedCause.confidence_score * 100)}% Match
                  </span>
                </div>
                <p className="text-[11px] text-indigo-800/90 dark:text-indigo-300/90 leading-relaxed">
                  {selectedCause.reasoning}
                </p>
              </div>
            )}

            {rankedCauses.length > 1 && (
              <div className="space-y-2">
                <span className="text-[11px] text-slate-400 dark:text-zinc-500 font-medium">Other Evaluated Candidates:</span>
                {rankedCauses.slice(1).map((c) => (
                  <div key={c.cause_id} className="p-2.5 rounded bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 flex items-center justify-between">
                    <span className="font-medium text-slate-700 dark:text-zinc-300 text-xs">{c.cause_name}</span>
                    <span className="font-mono text-[11px] text-slate-500 dark:text-zinc-400">{Math.round(c.confidence_score * 100)}% Match</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Section 6: Resolution Verification & Action Summary */}
          {selectedCause && (
            <div className="border border-slate-200 dark:border-zinc-800 rounded-xl p-4 bg-white dark:bg-zinc-900 print-break-inside-avoid">
              <h3 className="font-bold text-slate-900 dark:text-zinc-100 mb-3 uppercase tracking-wider text-[11px]">
                Executed Resolution Actions & Verification
              </h3>

              <div className="space-y-2 mb-3">
                {selectedCause.fix_steps.map((step) => {
                  const isChecked = Boolean(completedSteps[step.step_number]);
                  return (
                    <div key={step.step_number} className="p-2.5 rounded bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 flex items-start gap-2.5">
                      <div className={`w-4 h-4 rounded flex items-center justify-center shrink-0 mt-0.5 ${isChecked ? 'bg-emerald-600 text-white' : 'bg-slate-200 dark:bg-zinc-800 text-slate-400'}`}>
                        <CheckCircle2 className="w-3 h-3" />
                      </div>
                      <div>
                        <span className="font-semibold text-slate-800 dark:text-zinc-200 block text-xs">
                          Step {step.step_number}: {step.title}
                        </span>
                        <p className="text-[11px] text-slate-600 dark:text-zinc-400 leading-snug">{step.instruction}</p>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="p-3 rounded bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900 text-emerald-800 dark:text-emerald-300 text-[11px] flex items-center gap-2 font-medium">
                <ShieldCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
                Explicitly confirmed by user: Issue resolved following recommended fix steps.
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-950 flex justify-end print:hidden">

          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-200 dark:bg-zinc-800 hover:bg-slate-300 dark:hover:bg-zinc-700 text-slate-800 dark:text-zinc-200 text-xs font-medium transition-colors"
          >
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
};
