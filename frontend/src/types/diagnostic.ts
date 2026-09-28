export enum SafetyLevel {
  SAFE = "Safe",
  CAUTION = "Caution",
  ADVANCED = "Advanced"
}

export enum DomainEnum {
  PERFORMANCE = "performance",
  BOOT_FAILURE = "boot_failure",
  NETWORK = "network"
}

export enum ObservationSource {
  USER_INPUT = "user_input",
  SCREENSHOT = "screenshot",
  QUESTIONNAIRE = "questionnaire"
}

export type Observation = {
  key: string;
  value: boolean | number | string;
  confidence?: number;
  source?: ObservationSource;
  details?: string;
};

export type FixStep = {
  step_number: number;
  title: string;
  instruction: string;
  safety_level: SafetyLevel;
  warning_note?: string;
  verification_question: string;
};

export type RankedCause = {
  cause_id: string;
  cause_name: string;
  confidence_score: number;
  matched_symptoms: string[];
  reasoning: string;
  fix_steps: FixStep[];
};

export type SessionResponse = {
  session_id: string;
  domain: DomainEnum;
  observations: Observation[];
  ranked_causes: RankedCause[];
  status: string;
  created_at: string;
  updated_at: string;
};

export type DiagnosticRequest = {
  session_id?: string;
  domain: DomainEnum;
  text_input?: string;
  screenshot_base64?: string;
  observations: Observation[];
  top_process_name?: string;
};

export type DiagnosticResponse = {
  session_id?: string;
  domain: DomainEnum;
  processed_observations: Observation[];
  ranked_causes: RankedCause[];
  status: string;
};

export type QuestionCardItem = {
  id: string;
  symptomKey: string;
  questionText: string;
  category: "CPU" | "Memory" | "Disk" | "System" | "Power";
  description: string;
  type: "boolean" | "select";
  options?: { label: string; value: boolean | string }[];
};
