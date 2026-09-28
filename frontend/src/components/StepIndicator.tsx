import React from 'react';
import { Check } from 'lucide-react';

interface StepIndicatorProps {
  currentStep: number;
  onStepClick: (step: number) => void;
}

const steps = [
  { id: 1, title: 'Problem', desc: 'Describe issue' },
  { id: 2, title: 'Questions', desc: 'Symptom check' },
  { id: 3, title: 'Screenshot', desc: 'Task Manager' },
  { id: 4, title: 'Diagnosis', desc: 'Engine results' },
  { id: 5, title: 'Troubleshoot', desc: 'Fix & verify' },
];

export const StepIndicator: React.FC<StepIndicatorProps> = ({ currentStep, onStepClick }) => {
  return (
    <div className="w-full max-w-4xl mx-auto mb-8 px-4">
      <div className="relative flex items-center justify-between">
        {/* Background Track Line */}
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-0.5 bg-slate-200 dark:bg-zinc-800 -z-0 rounded-full" />
        <div
          className="absolute left-0 top-1/2 -translate-y-1/2 h-0.5 bg-indigo-600 dark:bg-indigo-500 -z-0 rounded-full transition-all duration-300"
          style={{ width: `${((currentStep - 1) / (steps.length - 1)) * 100}%` }}
        />

        {steps.map((step) => {
          const isCompleted = currentStep > step.id;
          const isCurrent = currentStep === step.id;

          return (
            <div key={step.id} className="flex flex-col items-center relative z-10">
              <button
                onClick={() => isCompleted && onStepClick(step.id)}
                disabled={!isCompleted && !isCurrent}
                className={`w-8 h-8 rounded-full flex items-center justify-center font-mono text-xs transition-all duration-200 ${
                  isCurrent
                    ? 'bg-indigo-600 text-white font-bold ring-4 ring-indigo-500/20 shadow-sm'
                    : isCompleted
                    ? 'bg-emerald-600 text-white hover:bg-emerald-500 cursor-pointer'
                    : 'bg-slate-100 dark:bg-zinc-900 text-slate-400 dark:text-zinc-600 border border-slate-200 dark:border-zinc-800 cursor-not-allowed'
                }`}
              >
                {isCompleted ? <Check className="w-4 h-4 stroke-[2.5]" /> : step.id}
              </button>
              <div className="mt-2 text-center hidden sm:block">
                <p
                  className={`text-xs font-medium ${
                    isCurrent
                      ? 'text-slate-900 dark:text-zinc-100 font-semibold'
                      : isCompleted
                      ? 'text-slate-700 dark:text-zinc-300'
                      : 'text-slate-400 dark:text-zinc-600'
                  }`}
                >
                  {step.title}
                </p>
                <p className="text-[10px] text-slate-400 dark:text-zinc-500">{step.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
