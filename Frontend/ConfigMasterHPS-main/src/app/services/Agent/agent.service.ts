import { Injectable, NgZone } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface GoalSummary {
  goal_id: number;
  client: string;
  action: string;
  folder: string;
  done: boolean;
  missing_count: number;
  created_at: string | null;
}

export interface MenuOption {
  id: string;
  label?: string;
  value: string;
  aliases?: string[];
}

export interface AgentMenu {
  title: string;
  options: MenuOption[];
}

export interface FormField {
  path: string;
  label: string;
}

export interface AgentForm {
  id: string;
  title: string;
  fields: FormField[];
  defaults?: { path: string; value: string }[];
  validators?: any[];
}

export interface AgentDecision {
  type: 'ASK' | 'ASK_MULTI' | 'DONE';
  path?: string;
  paths?: string[];
  question?: string;
  menu?: AgentMenu | null;
  form?: AgentForm | null;
}

export interface ProgressInfo {
  total_fields: number;
  filled_fields: number;
  missing_count: number;
  completion_pct: number;
  missing_paths: string[];
}

export interface CreateGoalResponse {
  goal_id: number;
  folder: string;
  decision: AgentDecision;
  progress: ProgressInfo;
}

export interface ChatResponse {
  decision: AgentDecision;
  progress: ProgressInfo;
  message?: string;
}

export interface GoalDetail {
  goal_id: number;
  folder: string;
  client: string;
  action: string;
  done: boolean;
  goal: string;
  progress: ProgressInfo;
  history: { agent: string; user: string }[];
  facts: any;
}

/** Events emitted during a streaming chat call */
export interface StreamToken {
  type: 'token';
  text: string;
}
export interface StreamMeta {
  type: 'meta';
  decision_type: string;
  progress: ProgressInfo;
}
export interface StreamDone {
  type: 'done';
  decision: AgentDecision;
  progress: ProgressInfo;
}
export type StreamEvent = StreamToken | StreamMeta | StreamDone;

@Injectable({
  providedIn: 'root',
})
export class AgentService {
  private baseUrl = environment.agentApiUrl;

  constructor(private http: HttpClient, private ngZone: NgZone) {}

  listGoals(): Observable<GoalSummary[]> {
    return this.http.get<GoalSummary[]>(`${this.baseUrl}/goals`);
  }

  createGoal(message: string): Observable<CreateGoalResponse> {
    return this.http.post<CreateGoalResponse>(`${this.baseUrl}/goals`, { message });
  }

  getGoal(goalId: number): Observable<GoalDetail> {
    return this.http.get<GoalDetail>(`${this.baseUrl}/goals/${goalId}`);
  }

  chat(goalId: number, message: string): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.baseUrl}/goals/${goalId}/chat`, { message });
  }

  /**
   * Streaming chat via SSE (Server-Sent Events).
   * Emits StreamEvent objects as the agent streams tokens.
   */
  chatStream(goalId: number, message: string): Observable<StreamEvent> {
    const subject = new Subject<StreamEvent>();

    fetch(`${this.baseUrl}/goals/${goalId}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    })
      .then((response) => {
        if (!response.ok || !response.body) {
          subject.error(new Error(`HTTP ${response.status}`));
          return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        const pump = (): Promise<void> =>
          reader.read().then(({ done, value }) => {
            if (done) {
              subject.complete();
              return;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() ?? '';

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const raw = line.slice(6).trim();
                if (raw) {
                  try {
                    const event: StreamEvent = JSON.parse(raw);
                    this.ngZone.run(() => subject.next(event));
                  } catch {
                    /* ignore malformed lines */
                  }
                }
              }
            }
            return pump();
          });

        pump().catch((err) => subject.error(err));
      })
      .catch((err) => subject.error(err));

    return subject.asObservable();
  }

  submitGoal(goalId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/goals/${goalId}/submit`, {});
  }

  generatePdf(goalId: number): Observable<Blob> {
    return this.http.post(`${this.baseUrl}/goals/${goalId}/pdf`, {}, {
      responseType: 'blob',
    });
  }

  deleteGoal(goalId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/goals/${goalId}`);
  }

  healthCheck(): Observable<any> {
    return this.http.get(`${this.baseUrl}/health`);
  }
}
