import React from 'react';
import { ArrowLeft, ArrowRight, Check, X, HelpCircle } from 'lucide-react';
import type { QuestionCardItem } from '../types/diagnostic';

interface QuestionnaireStepProps {
  answers: Record<string, boolean | undefined>;
  onAnswerChange: (symptomKey: string, value: boolean | undefined) => void;
  onBack: () => void;
  onNext: () => void;
}

const QUESTION_CARDS: QuestionCardItem[] = [
  {
    id: 'q_cpu',
    symptomKey: 'high_cpu_usage',
    questionText: 'Is your CPU usage frequently spiking to 80%-100% in Task Manager?',
    category: 'CPU',
    description: 'High processor workload caused by rogue processes, background scans, or heavy software.',
    type: 'boolean'
  },
  {
    id: 'q_ram',
    symptomKey: 'high_ram_usage',
    questionText: 'Is your RAM / Memory usage above 80% or experiencing memory leaks?',
    category: 'Memory',
    description: 'System memory exhaustion caused by browser tabs (Chrome) or memory leaking background apps.',
    type: 'boolean'
  },
  {
    id: 'q_disk',
    symptomKey: 'high_disk_usage',
    questionText: 'Is your Disk usage stuck at 100% or making continuous read/write sounds?',
    category: 'Disk',
    description: 'Disk saturation, mechanical HDD bottlenecks, or Windows Search indexing spikes.',
    type: 'boolean'
  },
  {
    id: 'q_freeze',
    symptomKey: 'app_freezing',
    questionText: 'Are specific applications freezing or showing "(Not Responding)" in the title bar?',
    category: 'System',
    description: 'Application hangs, thread lockups, or unresponsive software windows.',
    type: 'boolean'
  },
  {
    id: 'q_slowdown',
    symptomKey: 'general_slowdown',
    questionText: 'Is the overall OS experiencing sluggish response, cursor lag, or typing delays?',
    category: 'System',
    description: 'General system-wide latency across all desktop operations.',
    type: 'boolean'
  },
  {
    id: 'q_thermal',
    symptomKey: 'thermal_throttling',
    questionText: 'Is your computer running unusually hot, with loud fan noise or thermal throttling?',
    category: 'Power',
    description: 'CPU clock speed reduction due to thermal overheating or power plan limits.',
    type: 'boolean'
  }
];

export const QuestionnaireStep: React.FC<QuestionnaireStepProps> = ({
  answers,
  onAnswerChange,
  onBack,
  onNext
}) => {
  const answeredCount = Object.values(answers).filter((v) => v !== undefined).length;

  return (
    <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-6 shadow-sm max-w-4xl mx-auto transition-colors">
      {/* Header */}
      <div className="flex items-center justify-between mb-5 pb-4 border-b border-slate-100 dark:border-zinc-800">
        <div>
          <h2 className="text-base font-semibold text-slate-900 dark:text-zinc-100">
            Diagnostic Question Cards
          </h2>
          <p className="text-xs text-slate-500 dark:text-zinc-400">
            Answer symptom questions to refine cause ranking accuracy.
          </p>
        </div>
        <div className="px-2.5 py-1 rounded bg-slate-100 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 text-xs text-slate-700 dark:text-zinc-300 font-mono">
          {answeredCount}/{QUESTION_CARDS.length} Answered
        </div>
      </div>

      {/* Grid of Question Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {QUESTION_CARDS.map((card) => {
          const currentVal = answers[card.symptomKey];

          return (
            <div
              key={card.id}
              className={`p-4 rounded-lg border transition-all ${
                currentVal === true
                  ? 'bg-blue-50/70 dark:bg-zinc-800/80 border-blue-200 dark:border-zinc-700'
                  : currentVal === false
                  ? 'bg-slate-50 dark:bg-zinc-950/60 border-slate-200 dark:border-zinc-800/80 opacity-80'
                  : 'bg-slate-50/50 dark:bg-zinc-950/40 border-slate-200 dark:border-zinc-800 hover:border-slate-300 dark:hover:border-zinc-700'
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400 border border-slate-200 dark:border-zinc-700">
                  {card.category}
                </span>
                <span className="text-[11px] font-mono text-slate-400 dark:text-zinc-500">{card.symptomKey}</span>
              </div>

              <h4 className="text-xs font-semibold text-slate-900 dark:text-zinc-100 mb-1 leading-relaxed">
                {card.questionText}
              </h4>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400 mb-4">{card.description}</p>

              {/* Answer Controls */}
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => onAnswerChange(card.symptomKey, true)}
                  className={`flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-md text-xs font-medium border transition-all ${
                    currentVal === true
                      ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                      : 'bg-white dark:bg-zinc-800 hover:bg-slate-100 dark:hover:bg-zinc-700 text-slate-700 dark:text-zinc-300 border-slate-200 dark:border-zinc-700'
                  }`}
                >
                  <Check className="w-3.5 h-3.5" />
                  Yes
                </button>

                <button
                  type="button"
                  onClick={() => onAnswerChange(card.symptomKey, false)}
                  className={`flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-md text-xs font-medium border transition-all ${
                    currentVal === false
                      ? 'bg-slate-800 dark:bg-zinc-700 text-white border-slate-800 dark:border-zinc-700 shadow-sm'
                      : 'bg-white dark:bg-zinc-800 hover:bg-slate-100 dark:hover:bg-zinc-700 text-slate-700 dark:text-zinc-300 border-slate-200 dark:border-zinc-700'
                  }`}
                >
                  <X className="w-3.5 h-3.5" />
                  No
                </button>

                <button
                  type="button"
                  onClick={() => onAnswerChange(card.symptomKey, undefined)}
                  className={`flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-md text-xs font-medium border transition-all ${
                    currentVal === undefined
                      ? 'bg-slate-200 dark:bg-zinc-800 text-slate-800 dark:text-zinc-200 border-slate-300 dark:border-zinc-700 font-semibold'
                      : 'bg-white dark:bg-zinc-900 hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-500 dark:text-zinc-500 border-slate-200 dark:border-zinc-800'
                  }`}
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                  Skip
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-zinc-800">
        <button
          onClick={onBack}
          className="px-4 py-2 rounded-md bg-slate-100 dark:bg-zinc-800 hover:bg-slate-200 dark:hover:bg-zinc-700 text-slate-700 dark:text-zinc-300 text-xs font-medium flex items-center gap-2 transition-all border border-slate-200 dark:border-zinc-700"
        >
          <ArrowLeft className="w-4 h-4" />
          Back: Problem Description
        </button>

        <button
          onClick={onNext}
          className="px-5 py-2 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-sm flex items-center gap-2 transition-all"
        >
          Continue: Screenshot Upload
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
