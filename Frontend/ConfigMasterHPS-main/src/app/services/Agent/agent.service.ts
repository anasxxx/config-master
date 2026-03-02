import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
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

export interface AgentDecision {
  type: 'ASK' | 'ASK_MULTI' | 'DONE';
  path?: string;
  paths?: string[];
  question?: string;
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

@Injectable({
  providedIn: 'root',
})
export class AgentService {
  private baseUrl = environment.agentApiUrl;

  constructor(private http: HttpClient) {}

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
