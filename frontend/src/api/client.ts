import { DomainEnum } from '../types/diagnostic';
import type {
  SessionResponse,
  DiagnosticRequest,
  DiagnosticResponse,
  Observation
} from '../types/diagnostic';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = res.statusText;
    try {
      const data = await res.json();
      if (data && data.detail) {
        errorDetail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      }
    } catch {
      // Ignore JSON parse errors for non-JSON error bodies
    }
    throw new ApiError(res.status, errorDetail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  /**
   * Creates a new active troubleshooting session in Supabase.
   */
  async createSession(domain: DomainEnum = DomainEnum.PERFORMANCE): Promise<SessionResponse> {
    const res = await fetch(`${API_BASE}/session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain })
    });
    return handleResponse<SessionResponse>(res);
  },

  /**
   * Retrieves an existing session by ID from Supabase.
   */
  async getSession(sessionId: string): Promise<SessionResponse> {
    const res = await fetch(`${API_BASE}/session/${encodeURIComponent(sessionId)}`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    return handleResponse<SessionResponse>(res);
  },

  /**
   * Sends user text problem description to AI Assistance Layer to extract observations.
   */
  async parseText(text: string): Promise<Observation[]> {
    const res = await fetch(`${API_BASE}/diagnostic/parse-text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    return handleResponse<Observation[]>(res);
  },

  /**
   * Sends Task Manager screenshot (base64 or multipart) to AI Assistance Layer.
   */
  async parseScreenshot(screenshotBase64: string): Promise<Observation[]> {
    const res = await fetch(`${API_BASE}/diagnostic/parse-screenshot`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ screenshot_base64: screenshotBase64 })
    });
    return handleResponse<Observation[]>(res);
  },

  /**
   * Evaluates accumulated observations through the Expert Engine and persists state in Supabase.
   */
  async evaluateDiagnostic(requestPayload: DiagnosticRequest): Promise<DiagnosticResponse> {
    const res = await fetch(`${API_BASE}/diagnostic/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestPayload)
    });
    return handleResponse<DiagnosticResponse>(res);
  },

  /**
   * Updates session status in Supabase (e.g. to 'resolved').
   */
  async updateSessionStatus(sessionId: string, status: string = 'resolved'): Promise<SessionResponse> {
    const res = await fetch(`${API_BASE}/session/${encodeURIComponent(sessionId)}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    return handleResponse<SessionResponse>(res);
  }
};
