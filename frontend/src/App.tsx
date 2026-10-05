import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { StepIndicator } from './components/StepIndicator';
import { ProblemInputStep } from './components/ProblemInputStep';
import { QuestionnaireStep } from './components/QuestionnaireStep';
import { ScreenshotUploadStep } from './components/ScreenshotUploadStep';
import { DiagnosisResultStep } from './components/DiagnosisResultStep';
import { TroubleshootingGuideStep } from './components/TroubleshootingGuideStep';
import { DiagnosisReportModal } from './components/DiagnosisReportModal';

import { api, ApiError } from './api/client';
import { DomainEnum, ObservationSource } from './types/diagnostic';
import type { Observation, RankedCause, DiagnosticRequest } from './types/diagnostic';
import { detectDomainIntent } from './utils/domainIntent';

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
  const [currentDomain, setCurrentDomain] = useState<DomainEnum>(DomainEnum.PERFORMANCE);
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

  // Report & Resolution States
  const [isResolved, setIsResolved] = useState<boolean>(false);
  const [resolvedCompletedSteps, setResolvedCompletedSteps] = useState<Record<number, boolean>>({});
  const [resolvedAtTimestamp, setResolvedAtTimestamp] = useState<string>('');
  const [isReportOpen, setIsReportOpen] = useState<boolean>(false);

  // Status & Error States
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  // Domain suggestion when detected intent differs from selected domain
  const [suggestedDomain, setSuggestedDomain] = useState<DomainEnum | null>(null);

  const STORAGE_KEY = 'fixit_saarthi_active_state_v1';

  // Auto-sync transient UI state to sessionStorage for seamless browser refresh
  useEffect(() => {
    if (sessionId) {
      try {
        sessionStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({
            sessionId,
            currentDomain,
            currentStep,
            textInput,
            answers,
            processedObservations,
            rankedCauses,
            selectedCause,
            isResolved,
            resolvedCompletedSteps,
            resolvedAtTimestamp
          })
        );
      } catch {
        // Storage full or unavailable
      }
    }
  }, [
    sessionId,
    currentDomain,
    currentStep,
    textInput,
    answers,
    processedObservations,
    rankedCauses,
    selectedCause,
    isResolved,
    resolvedCompletedSteps,
    resolvedAtTimestamp
  ]);

  // Initialize Session / Restore Session (from URL query param or sessionStorage) on mount
  useEffect(() => {
    const initOrRestoreSession = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const sharedSessionId = urlParams.get('session_id');

      if (sharedSessionId && sharedSessionId.trim()) {
        setIsLoading(true);
        setError(null);
        try {
          const session = await api.getSession(sharedSessionId.trim());
          setSessionId(session.session_id);
          setCurrentDomain(session.domain || DomainEnum.PERFORMANCE);
          setProcessedObservations(session.observations || []);
          setRankedCauses(session.ranked_causes || []);

          if (session.observations && session.observations.length > 0) {
            const restoredAnswers: Record<string, boolean | undefined> = {};
            session.observations.forEach((obs) => {
              if (typeof obs.value === 'boolean') {
                restoredAnswers[obs.key] = obs.value;
              }
            });
            setAnswers(restoredAnswers);
          }

          if (session.ranked_causes && session.ranked_causes.length > 0) {
            setSelectedCause(session.ranked_causes[0]);
            const isRes = session.status === 'resolved';
            setIsResolved(isRes);
            setCurrentStep(isRes ? 5 : 4);
          } else if (session.observations && session.observations.length > 0) {
            setCurrentStep(2);
          } else {
            setCurrentStep(1);
          }
        } catch (err) {
          window.history.replaceState({}, '', window.location.pathname);
          const detail = err instanceof ApiError ? err.detail : 'The shared troubleshooting session could not be loaded.';
          setError(`${detail} A new session has been started.`);

          try {
            const newSession = await api.createSession(currentDomain);
            setSessionId(newSession.session_id);
          } catch {
            setSessionId(null);
          }
        } finally {
          setIsLoading(false);
        }
      } else {
        // Check sessionStorage for active session state on browser refresh
        const rawSaved = sessionStorage.getItem(STORAGE_KEY);
        if (rawSaved) {
          try {
            const saved = JSON.parse(rawSaved);
            if (saved && saved.sessionId) {
              // Verify session is still valid with backend
              const session = await api.getSession(saved.sessionId);
              setSessionId(session.session_id);
              setCurrentDomain(saved.currentDomain || session.domain || DomainEnum.PERFORMANCE);
              setTextInput(saved.textInput || '');
              setAnswers(saved.answers || {});
              setProcessedObservations(session.observations && session.observations.length > 0 ? session.observations : (saved.processedObservations || []));
              setRankedCauses(session.ranked_causes && session.ranked_causes.length > 0 ? session.ranked_causes : (saved.rankedCauses || []));
              setSelectedCause(saved.selectedCause || (session.ranked_causes && session.ranked_causes.length > 0 ? session.ranked_causes[0] : null));
              setIsResolved(saved.isResolved || session.status === 'resolved');
              setResolvedCompletedSteps(saved.resolvedCompletedSteps || {});
              setResolvedAtTimestamp(saved.resolvedAtTimestamp || session.updated_at || '');
              setCurrentStep(saved.currentStep || 1);
              return;
            }
          } catch {
            sessionStorage.removeItem(STORAGE_KEY);
          }
        }

        // No stored state or invalid: create new active session
        try {
          const session = await api.createSession(currentDomain);
          setSessionId(session.session_id);
        } catch (err) {
          console.warn('Could not initialize Supabase session:', err);
        }
      }
    };

    initOrRestoreSession();
  }, []);

  const handleSelectDomain = async (domain: DomainEnum) => {
    if (domain === currentDomain) return;
    sessionStorage.removeItem(STORAGE_KEY);
    setCurrentDomain(domain);
    setIsLoading(true);
    setError(null);
    try {
      const session = await api.createSession(domain);
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
      setSuggestedDomain(null);
      setIsResolved(false);
      setResolvedCompletedSteps({});
      setResolvedAtTimestamp('');
      setCurrentStep(1);
      setIsLoading(false);
    }
  };

  const handleResetSession = async () => {
    setIsLoading(true);
    setError(null);
    sessionStorage.removeItem(STORAGE_KEY);

    if (window.location.search) {
      window.history.replaceState({}, '', window.location.pathname);
    }

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
      setSuggestedDomain(null);
      setIsResolved(false);
      setResolvedCompletedSteps({});
      setResolvedAtTimestamp('');
      setCurrentStep(1);
      setIsLoading(false);
    }
  };

  // Out-of-Domain Scope Guard & Internal AI Text Extraction
  const handleProceedFromProblemStep = async () => {
    const trimmed = textInput.trim();
    setSuggestedDomain(null);
    if (!trimmed) {
      setError("Please describe your computer problem before continuing.");
      setCurrentStep(1);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const obs = await api.parseText(trimmed);
      setExtractedTextObs(obs);
      setError(null);

      // Domain-intent detection: check if text clearly belongs to a different domain
      const detected = detectDomainIntent(trimmed);
      if (detected && detected !== currentDomain) {
        // Show suggestion banner — do NOT advance step yet
        setSuggestedDomain(detected);
      } else {
        setCurrentStep(2); // proceed normally
      }
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

  /**
   * User accepts the domain suggestion: switch domain, create new session,
   * preserve the text input, then advance to questions.
   */
  const handleAcceptDomainSuggestion = async (domain: DomainEnum) => {
    setSuggestedDomain(null);
    setIsLoading(true);
    setError(null);
    try {
      const session = await api.createSession(domain);
      setSessionId(session.session_id);
      setCurrentDomain(domain);
      // Re-parse text under new domain to get domain-relevant observations
      const obs = await api.parseText(textInput.trim());
      setExtractedTextObs(obs);
      setAnswers({});
      setCurrentStep(2);
    } catch {
      // If anything fails, still switch domain and proceed
      setCurrentDomain(domain);
      setAnswers({});
      setCurrentStep(2);
    } finally {
      setIsLoading(false);
    }
  };

  /** User dismisses the suggestion: keep current domain and proceed to questions. */
  const handleDismissDomainSuggestion = () => {
    setSuggestedDomain(null);
    setCurrentStep(2);
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

  const handleConfirmResolved = async (completedStepsMap: Record<number, boolean>) => {
    setIsResolved(true);
    setResolvedCompletedSteps(completedStepsMap);
    const nowIso = new Date().toISOString();
    setResolvedAtTimestamp(nowIso);
    if (sessionId) {
      try {
        await api.updateSessionStatus(sessionId, 'resolved');
      } catch (err) {
        console.warn('Failed to update session status on backend:', err);
      }
    }
  };

  const handleOpenReport = (completedStepsMap: Record<number, boolean>) => {
    setResolvedCompletedSteps(completedStepsMap);
    setIsReportOpen(true);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-zinc-950 text-slate-900 dark:text-zinc-100 flex flex-col font-sans transition-colors duration-200">
      {/* Navbar Header */}
      <Navbar
        currentDomain={currentDomain}
        onSelectDomain={handleSelectDomain}
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
            currentDomain={currentDomain}
            textInput={textInput}
            onChangeText={(t) => { setTextInput(t); setSuggestedDomain(null); }}
            isLoading={isLoading}
            error={error}
            onProceed={handleProceedFromProblemStep}
            suggestedDomain={suggestedDomain}
            onAcceptSuggestion={handleAcceptDomainSuggestion}
            onDismissSuggestion={handleDismissDomainSuggestion}
          />
        )}

        {currentStep === 2 && (
          <QuestionnaireStep
            currentDomain={currentDomain}
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
            onConfirmResolved={handleConfirmResolved}
            onOpenReport={handleOpenReport}
            isResolvedInitial={isResolved}
          />
        )}
      </main>

      {/* Diagnosis Report Modal */}
      <DiagnosisReportModal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        sessionId={sessionId}
        domain={currentDomain}
        problemDescription={textInput}
        answers={answers}
        processedObservations={processedObservations}
        rankedCauses={rankedCauses}
        selectedCause={selectedCause}
        completedSteps={resolvedCompletedSteps}
        resolvedAt={resolvedAtTimestamp || new Date().toISOString()}
      />

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-zinc-800 bg-white/50 dark:bg-zinc-950/50 py-4 text-center text-xs text-slate-500 dark:text-zinc-500">
        <p>FixIT Saarthi — Expert Computer Diagnostic System</p>
      </footer>
    </div>
  );
};

export default App;
