import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { StepIndicator } from './components/StepIndicator';
import { ProblemInputStep } from './components/ProblemInputStep';
import { QuestionnaireStep } from './components/QuestionnaireStep';
import { ScreenshotUploadStep } from './components/ScreenshotUploadStep';
import { DiagnosisResultStep } from './components/DiagnosisResultStep';
import { TroubleshootingGuideStep } from './components/TroubleshootingGuideStep';

import { api, ApiError } from './api/client';
import { DomainEnum, ObservationSource } from './types/diagnostic';
import type { Observation, RankedCause, DiagnosticRequest } from './types/diagnostic';

export const App: React.FC = () => {
  // Theme State (Light / Dark mode persisted in localStorage)
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('theme');
    if (saved === 'light' || saved === 'dark') return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
      root.classList.remove('light');
    } else {
      root.classList.add('light');
      root.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const handleToggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  // Session & Domain State
  const [currentDomain] = useState<DomainEnum>(DomainEnum.PERFORMANCE);
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Workflow Progression (Step 1-5)
  const [currentStep, setCurrentStep] = useState<number>(1);

  // Input Data States
  const [textInput, setTextInput] = useState<string>('');
  const [answers, setAnswers] = useState<Record<string, boolean | undefined>>({});
  const [screenshotBase64, setScreenshotBase64] = useState<string | null>(null);

  // Observations & Engine Results
  const [extractedTextObs, setExtractedTextObs] = useState<Observation[]>([]);
  const [extractedScreenshotObs, setExtractedScreenshotObs] = useState<Observation[]>([]);
  const [processedObservations, setProcessedObservations] = useState<Observation[]>([]);
  const [rankedCauses, setRankedCauses] = useState<RankedCause[]>([]);
  const [selectedCause, setSelectedCause] = useState<RankedCause | null>(null);

  // Status & Error States
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize Session on mount
  useEffect(() => {
    const initSession = async () => {
      try {
        const session = await api.createSession(currentDomain);
        setSessionId(session.session_id);
      } catch (err) {
        console.warn('Could not initialize Supabase session:', err);
      }
    };
    initSession();
  }, [currentDomain]);

  const handleResetSession = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const session = await api.createSession(currentDomain);
      setSessionId(session.session_id);
    } catch {
      setSessionId(null);
    } finally {
      setTextInput('');
      setAnswers({});
      setScreenshotBase64(null);
      setExtractedTextObs([]);
      setExtractedScreenshotObs([]);
      setProcessedObservations([]);
      setRankedCauses([]);
      setSelectedCause(null);
      setCurrentStep(1);
      setIsLoading(false);
    }
  };

  // Out-of-Domain Scope Guard & Internal AI Text Extraction
  const handleProceedFromProblemStep = async () => {
    const trimmed = textInput.trim();
    if (!trimmed) {
      setError(null);
      setCurrentStep(2);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const obs = await api.parseText(trimmed);
      setExtractedTextObs(obs);
      setError(null);
      setCurrentStep(2); // Proceed to Questions only on valid domain!
    } catch (err) {
      if (err instanceof ApiError) {
        const lowerDetail = err.detail.toLowerCase();
        if (
          err.status === 400 ||
          lowerDetail.includes('out of scope') ||
          lowerDetail.includes('prompt injection') ||
          lowerDetail.includes('computer troubleshooting')
        ) {
          setError("This doesn't appear to be a supported computer troubleshooting problem.");
        } else {
          setError(err.detail);
        }
      } else {
        setError("This doesn't appear to be a supported computer troubleshooting problem.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Diagnostic Questionnaire Handlers
  const handleAnswerChange = (symptomKey: string, value: boolean | undefined) => {
    setAnswers((prev) => ({ ...prev, [symptomKey]: value }));
  };

  // AI Screenshot OCR Extraction
  const handleParseScreenshot = async (base64Str: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const obs = await api.parseScreenshot(base64Str);
      setExtractedScreenshotObs(obs);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError('Failed to analyze screenshot image.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Run Expert Engine Evaluation (Step 3 -> Step 4)
  const handleRunDiagnosis = async () => {
    setIsLoading(true);
    setError(null);

    // Accumulate questionnaire observations
    const questionnaireObs: Observation[] = [];
    Object.entries(answers).forEach(([key, val]) => {
      if (val !== undefined) {
        questionnaireObs.push({
          key,
          value: val,
          confidence: 1.0,
          source: ObservationSource.QUESTIONNAIRE
        });
      }
    });

    const payload: DiagnosticRequest = {
      session_id: sessionId || undefined,
      domain: currentDomain,
      text_input: textInput.trim() || undefined,
      screenshot_base64: screenshotBase64 || undefined,
      observations: questionnaireObs
    };

    try {
      const res = await api.evaluateDiagnostic(payload);
      setProcessedObservations(res.processed_observations);
      setRankedCauses(res.ranked_causes);
      if (res.ranked_causes.length > 0) {
        setSelectedCause(res.ranked_causes[0]);
      }
      setCurrentStep(4); // Advance to Diagnosis Result
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError('Failed to evaluate expert diagnostic engine.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-zinc-950 text-slate-900 dark:text-zinc-100 flex flex-col font-sans transition-colors duration-200">
      {/* Navbar Header */}
      <Navbar
        currentDomain={currentDomain}
        sessionId={sessionId}
        onResetSession={handleResetSession}
        theme={theme}
        onToggleTheme={handleToggleTheme}
      />

      {/* Main Workflow Container */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Step Indicator */}
        <StepIndicator
          currentStep={currentStep}
          onStepClick={(step) => setCurrentStep(step)}
        />

        {/* Workflow Steps */}
        {currentStep === 1 && (
          <ProblemInputStep
            textInput={textInput}
            onChangeText={setTextInput}
            isLoading={isLoading}
            error={error}
            onProceed={handleProceedFromProblemStep}
          />
        )}

        {currentStep === 2 && (
          <QuestionnaireStep
            answers={answers}
            onAnswerChange={handleAnswerChange}
            onBack={() => setCurrentStep(1)}
            onNext={() => setCurrentStep(3)}
          />
        )}

        {currentStep === 3 && (
          <ScreenshotUploadStep
            screenshotBase64={screenshotBase64}
            onScreenshotChange={setScreenshotBase64}
            onParseScreenshot={handleParseScreenshot}
            screenshotObservations={extractedScreenshotObs}
            isLoading={isLoading}
            error={error}
            onBack={() => setCurrentStep(2)}
            onRunDiagnosis={handleRunDiagnosis}
          />
        )}

        {currentStep === 4 && (
          <DiagnosisResultStep
            rankedCauses={rankedCauses}
            observations={processedObservations}
            onSelectCause={(cause) => {
              setSelectedCause(cause);
              setCurrentStep(5);
            }}
            onBackToInputs={() => setCurrentStep(1)}
          />
        )}

        {currentStep === 5 && selectedCause && (
          <TroubleshootingGuideStep
            cause={selectedCause}
            allCauses={rankedCauses}
            onSelectOtherCause={(cause) => setSelectedCause(cause)}
            onBackToDiagnosis={() => setCurrentStep(4)}
            onResetSession={handleResetSession}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-zinc-800 bg-white/50 dark:bg-zinc-950/50 py-4 text-center text-xs text-slate-500 dark:text-zinc-500">
        <p>FixIT Saarthi — Expert Computer Diagnostic System</p>
      </footer>
    </div>
  );
};

export default App;
