import { Component, HostListener, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { NgClass, NgFor, NgIf } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { AuthService } from '../services/Auth/auth.service';
import {
  AgentService,
  GoalSummary,
  AgentDecision,
  ProgressInfo,
  GoalDetail,
} from '../services/Agent/agent.service';

interface ChatMessage {
  role: 'agent' | 'user' | 'system';
  text: string;
  timestamp: Date;
  paths?: string[];
}

@Component({
  selector: 'app-ai-agent',
  standalone: true,
  imports: [
    TranslateModule,
    NgClass,
    NgFor,
    NgIf,
    RouterModule,
    FormsModule,
  ],
  templateUrl: './ai-agent.component.html',
  styleUrls: ['./ai-agent.component.scss'],
})
export class AiAgentComponent implements OnInit, AfterViewChecked {
  @ViewChild('chatContainer') private chatContainer!: ElementRef;
  @ViewChild('messageInput') private messageInput!: ElementRef;

  // Sidebar
  sidebarExpanded = false;
  isMobile = false;
  username = '';
  activityExpanded = false;

  // Goals list
  goals: GoalSummary[] = [];
  isLoadingGoals = true;

  // Active chat
  activeGoalId: number | null = null;
  activeGoalDetail: GoalDetail | null = null;
  messages: ChatMessage[] = [];
  userInput = '';
  isTyping = false;
  currentDecision: AgentDecision | null = null;
  progress: ProgressInfo | null = null;

  // New goal
  showNewGoalInput = false;
  newGoalMessage = '';
  isCreatingGoal = false;

  // Submission
  isSubmitting = false;
  submissionResult: any = null;

  constructor(
    private router: Router,
    private translate: TranslateService,
    private authService: AuthService,
    private agentService: AgentService
  ) {}

  ngOnInit() {
    this.checkScreenSize();
    this.getUserInfo();
    this.loadGoals();
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  // ─── Goals Management ──────────────────────────────────────────────────────
  loadGoals() {
    this.isLoadingGoals = true;
    this.agentService.listGoals().subscribe({
      next: (goals) => {
        this.goals = goals.sort((a, b) => b.goal_id - a.goal_id);
        this.isLoadingGoals = false;
      },
      error: (err) => {
        console.error('Failed to load goals:', err);
        this.isLoadingGoals = false;
        this.messages = [{
          role: 'system',
          text: this.translate.instant('agent.errorLoadGoals'),
          timestamp: new Date(),
        }];
      },
    });
  }

  startNewGoal() {
    this.showNewGoalInput = true;
    this.newGoalMessage = '';
    this.activeGoalId = null;
    this.activeGoalDetail = null;
    this.messages = [{
      role: 'agent',
      text: this.translate.instant('agent.createPrompt'),
      timestamp: new Date(),
    }];
    this.progress = null;
    this.currentDecision = null;
    this.submissionResult = null;
  }

  createGoal() {
    if (!this.newGoalMessage.trim()) return;
    this.isCreatingGoal = true;

    this.messages.push({
      role: 'user',
      text: this.newGoalMessage,
      timestamp: new Date(),
    });

    const msg = this.newGoalMessage;
    this.newGoalMessage = '';
    this.showNewGoalInput = false;

    this.agentService.createGoal(msg).subscribe({
      next: (res) => {
        this.activeGoalId = res.goal_id;
        this.progress = res.progress;
        this.currentDecision = res.decision;
        this.isCreatingGoal = false;
        this.loadGoals(); // refresh sidebar list

        this.messages.push({
          role: 'system',
          text: this.translate.instant('agent.goalCreated', { folder: res.folder }),
          timestamp: new Date(),
        });

        if (res.decision.type === 'DONE') {
          this.messages.push({
            role: 'agent',
            text: this.translate.instant('agent.allComplete'),
            timestamp: new Date(),
          });
        } else {
          this.messages.push({
            role: 'agent',
            text: res.decision.question || '',
            timestamp: new Date(),
            paths: res.decision.paths || (res.decision.path ? [res.decision.path] : []),
          });
        }
      },
      error: (err) => {
        this.isCreatingGoal = false;
        this.messages.push({
          role: 'system',
          text: this.translate.instant('agent.errorCreate'),
          timestamp: new Date(),
        });
      },
    });
  }

  openGoal(goal: GoalSummary) {
    this.activeGoalId = goal.goal_id;
    this.showNewGoalInput = false;
    this.submissionResult = null;
    this.messages = [];
    this.isTyping = true;

    this.agentService.getGoal(goal.goal_id).subscribe({
      next: (detail) => {
        this.activeGoalDetail = detail;
        this.progress = detail.progress;
        this.isTyping = false;

        // Replay history
        for (const h of detail.history) {
          if (h.agent && h.agent !== 'DONE') {
            this.messages.push({
              role: 'agent',
              text: h.agent,
              timestamp: new Date(),
            });
          }
          if (h.user) {
            this.messages.push({
              role: 'user',
              text: h.user,
              timestamp: new Date(),
            });
          }
        }

        if (detail.done) {
          this.messages.push({
            role: 'agent',
            text: this.translate.instant('agent.allComplete'),
            timestamp: new Date(),
          });
          this.currentDecision = { type: 'DONE' };
        } else {
          // Get next question
          this.getNextQuestion();
        }
      },
      error: () => {
        this.isTyping = false;
        this.messages.push({
          role: 'system',
          text: this.translate.instant('agent.errorLoad'),
          timestamp: new Date(),
        });
      },
    });
  }

  getNextQuestion() {
    if (!this.activeGoalId) return;
    // Send empty chat to get the current question
    this.agentService.getGoal(this.activeGoalId).subscribe({
      next: (detail) => {
        this.progress = detail.progress;
        if (!detail.done) {
          // We need to trigger brain_step with no user_msg to get the current question
          // The getGoal doesn't give us the next question, so we read state and infer
          // Actually, let's just ask brain for next question by looking at missing fields
          this.agentService.chat(this.activeGoalId!, '.').subscribe({
            next: (res) => {
              this.progress = res.progress;
              this.currentDecision = res.decision;
              if (res.decision.type !== 'DONE' && res.decision.question) {
                this.messages.push({
                  role: 'agent',
                  text: res.decision.question,
                  timestamp: new Date(),
                  paths: res.decision.paths || (res.decision.path ? [res.decision.path] : []),
                });
              }
            }
          });
        }
      }
    });
  }

  deleteGoal(goal: GoalSummary, event: Event) {
    event.stopPropagation();
    if (!confirm(this.translate.instant('agent.confirmDelete', { folder: goal.folder }))) return;

    this.agentService.deleteGoal(goal.goal_id).subscribe({
      next: () => {
        this.goals = this.goals.filter(g => g.goal_id !== goal.goal_id);
        if (this.activeGoalId === goal.goal_id) {
          this.activeGoalId = null;
          this.messages = [];
          this.progress = null;
        }
      },
    });
  }

  // ─── Chat ──────────────────────────────────────────────────────────────────
  sendMessage() {
    if (!this.userInput.trim() || !this.activeGoalId || this.isTyping) return;

    const text = this.userInput.trim();
    this.userInput = '';

    this.messages.push({
      role: 'user',
      text,
      timestamp: new Date(),
    });

    this.isTyping = true;

    this.agentService.chat(this.activeGoalId, text).subscribe({
      next: (res) => {
        this.isTyping = false;
        this.progress = res.progress;
        this.currentDecision = res.decision;

        if (res.decision.type === 'DONE') {
          this.messages.push({
            role: 'agent',
            text: this.translate.instant('agent.allComplete'),
            timestamp: new Date(),
          });
          this.loadGoals();
        } else if (res.decision.question) {
          this.messages.push({
            role: 'agent',
            text: res.decision.question,
            timestamp: new Date(),
            paths: res.decision.paths || (res.decision.path ? [res.decision.path] : []),
          });
        }

        // Focus input
        setTimeout(() => this.messageInput?.nativeElement?.focus(), 100);
      },
      error: (err) => {
        this.isTyping = false;
        this.messages.push({
          role: 'system',
          text: this.translate.instant('agent.errorChat'),
          timestamp: new Date(),
        });
      },
    });
  }

  onKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      if (this.showNewGoalInput) {
        this.createGoal();
      } else {
        this.sendMessage();
      }
    }
  }

  // ─── Actions ───────────────────────────────────────────────────────────────
  submitToBackend() {
    if (!this.activeGoalId) return;
    this.isSubmitting = true;
    this.submissionResult = null;

    this.agentService.submitGoal(this.activeGoalId).subscribe({
      next: (res) => {
        this.isSubmitting = false;
        this.submissionResult = { success: true, data: res };
        this.messages.push({
          role: 'system',
          text: this.translate.instant('agent.submitSuccess'),
          timestamp: new Date(),
        });
      },
      error: (err) => {
        this.isSubmitting = false;
        this.submissionResult = { success: false, error: err.error?.detail || err.message };
        this.messages.push({
          role: 'system',
          text: this.translate.instant('agent.submitError') + ': ' + (err.error?.detail || err.message),
          timestamp: new Date(),
        });
      },
    });
  }

  generatePdf() {
    if (!this.activeGoalId) return;
    this.agentService.generatePdf(this.activeGoalId).subscribe({
      next: (blob: Blob) => {
        const url = URL.createObjectURL(blob);
        window.open(url, '_blank');
        setTimeout(() => URL.revokeObjectURL(url), 60000);
        this.messages.push({
          role: 'system',
          text: this.translate.instant('agent.pdfGenerated'),
          timestamp: new Date(),
        });
      },
      error: () => {
        this.messages.push({
          role: 'system',
          text: this.translate.instant('agent.pdfError'),
          timestamp: new Date(),
        });
      },
    });
  }

  // ─── Sidebar helpers ───────────────────────────────────────────────────────
  toggleSidebar() {
    this.sidebarExpanded = !this.sidebarExpanded;
  }

  toggleActivity() {
    this.activityExpanded = !this.activityExpanded;
  }

  @HostListener('window:resize')
  checkScreenSize() {
    if (typeof window !== 'undefined') {
      this.isMobile = window.innerWidth < 768;
      if (this.isMobile) this.sidebarExpanded = false;
    }
  }

  getUserInfo() {
    if (this.authService.isFullUser()) {
      this.username = 'Full Profile';
    } else if (this.authService.isDemoUser()) {
      this.username = 'Demo Profile';
    } else {
      this.username = 'User';
    }
  }

  getUserInitials(): string {
    return this.username
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase();
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  private scrollToBottom() {
    try {
      if (this.chatContainer) {
        this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;
      }
    } catch {}
  }

  getGoalStatusClass(goal: GoalSummary): string {
    if (goal.done) return 'status-done';
    if (goal.missing_count <= 5) return 'status-almost';
    return 'status-progress';
  }

  getGoalStatusIcon(goal: GoalSummary): string {
    if (goal.done) return 'bi-check-circle-fill';
    if (goal.missing_count <= 5) return 'bi-hourglass-split';
    return 'bi-circle';
  }
}
