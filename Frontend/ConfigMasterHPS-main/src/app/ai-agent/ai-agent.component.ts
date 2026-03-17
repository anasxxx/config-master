import { Component, HostListener, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { NgClass, NgFor, NgIf, TitleCasePipe } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { AuthService } from '../services/Auth/auth.service';
import {
  AgentService,
  GoalSummary,
  AgentDecision,
  AgentMenu,
  AgentForm,
  ProgressInfo,
  GoalDetail,
  StreamEvent,
} from '../services/Agent/agent.service';

interface ChatMessage {
  role: 'agent' | 'user' | 'system';
  text: string;
  timestamp: Date;
  paths?: string[];
  menu?: AgentMenu | null;
  form?: AgentForm | null;
  /** True while the agent is streaming tokens into this message */
  streaming?: boolean;
}

@Component({
  selector: 'app-ai-agent',
  standalone: true,
  imports: [
    TranslateModule,
    NgClass,
    NgFor,
    NgIf,
    TitleCasePipe,
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

  // Menu & Form
  activeMenu: AgentMenu | null = null;
  activeForm: AgentForm | null = null;
  formValues: Record<string, string> = {};

  // Param help (+ button): show description, input type, example
  helpPath: string | null = null;
  readonly PARAM_HELP: Record<string, { description: string; inputType: string; example: string }> = {
    'bank.name': {
      description: 'Nom officiel de la banque (ex: affiché sur les agences et documents).',
      inputType: 'Texte (lettres et espaces, max 40 caractères)',
      example: 'Sahara Bank, Atlasia',
    },
    'bank.country': {
      description: 'Pays où la banque est implantée.',
      inputType: 'Texte (nom du pays, max 50 caractères)',
      example: 'Maroc, France',
    },
    'bank.currency': {
      description: 'Devise principale de la banque (code ISO à 3 lettres).',
      inputType: 'Code devise 3 lettres majuscules',
      example: 'MAD, EUR, USD',
    },
    'bank.bank_code': {
      description: 'Code unique de la banque dans le système (format PowerCard).',
      inputType: 'Exactement 6 caractères alphanumériques majuscules',
      example: 'SAH01X, ATL01X',
    },
    'bank.resources': {
      description: 'Ressources / modules à activer (MCD, UPI, HOST_BANK, VISA_BASE1, etc.).',
      inputType: 'Choix multiples (menu ou liste séparée par des virgules)',
      example: 'MCD_MDS, VISA_BASE1 ou 1, 2',
    },
    'bank.agencies.0.agency_name': {
      description: 'Nom de l\'agence ou du guichet.',
      inputType: 'Texte (max 40 caractères)',
      example: 'Agence Casablanca Centre, Maarif',
    },
    'bank.agencies.0.agency_code': {
      description: 'Code unique de l\'agence (format PowerCard).',
      inputType: 'Exactement 6 caractères alphanumériques majuscules',
      example: 'AG001X, 020001',
    },
    'bank.agencies.0.city': {
      description: 'Ville où se trouve l\'agence.',
      inputType: 'Texte (nom de la ville, max 32 caractères)',
      example: 'Casablanca, Paris',
    },
    'bank.agencies.0.city_code': {
      description: 'Code de la ville (identifiant interne).',
      inputType: '1 à 5 caractères alphanumériques majuscules',
      example: 'CASA, 001',
    },
    'bank.agencies.0.region': {
      description: 'Région géographique ou administrative de l\'agence.',
      inputType: 'Texte (max 30 caractères)',
      example: 'Casablanca-Settat, Île-de-France',
    },
    'bank.agencies.0.region_code': {
      description: 'Code de la région (identifiant interne).',
      inputType: '1 à 3 caractères alphanumériques majuscules',
      example: 'CS, 01',
    },
    'cards.0.card_info.bin': {
      description: 'BIN (Bank Identification Number) de la carte, 6 à 11 chiffres.',
      inputType: 'Numérique, 6 à 11 chiffres',
      example: '445566, 12345678901',
    },
    'cards.0.card_info.network': {
      description: 'Réseau de la carte (VISA, Mastercard, etc.).',
      inputType: 'Code réseau (VISA, MCRD, AMEX, etc.)',
      example: 'VISA, MCRD, AMEX',
    },
    'cards.0.card_info.product_type': {
      description: 'Type de produit carte (débit, crédit, prépayée).',
      inputType: 'DEBIT, CREDIT ou PREPAID',
      example: 'DEBIT, CREDIT',
    },
    'cards.0.card_info.plastic_type': {
      description: 'Type de support physique de la carte.',
      inputType: 'PVC, PETG, MTL, VRT, OTH',
      example: 'PVC, VRT (virtuelle)',
    },
    'cards.0.card_info.product_code': {
      description: 'Code produit carte (3 caractères).',
      inputType: 'Exactement 3 caractères majuscules',
      example: 'VCL, MCR',
    },
    'cards.0.card_info.card_description': {
      description: 'Nom ou description du produit carte.',
      inputType: 'Texte (max 40 caractères)',
      example: 'Visa Classic Internationale',
    },
    'cards.0.card_info.pvk_index': {
      description: 'Index PVK utilisé pour la génération et la vérification du PIN.',
      inputType: 'Entier positif (index de clé, défini par le schéma HSM)',
      example: '1, 2',
    },
    'cards.0.card_info.service_code': {
      description: 'Service code ISO de 3 chiffres indiqué dans la piste de la carte (contrôles d’acceptation).',
      inputType: 'Exactement 3 chiffres',
      example: '201, 221',
    },
    'cards.0.card_info.expiration': {
      description: 'Durée de validité de la carte avant expiration.',
      inputType: 'Nombre de mois ou années selon vos standards internes',
      example: '36 (mois), 48',
    },
    'cards.0.card_info.pre_expiration': {
      description: 'Délai avant expiration pour déclencher le renouvellement automatique.',
      inputType: 'Nombre de jours ou de mois (entier ≥ 0)',
      example: '60, 90',
    },
    'cards.0.fees.billing_event': {
      description: "Moment où les frais de carte sont facturés (émission, renouvellement ou remplacement).",
      inputType: 'Code numérique: 1 = Emission, 2 = Renouvellement, 3 = Remplacement',
      example: '1, 2, 3',
    },
    'cards.0.fees.grace_period': {
      description: 'Nombre de jours de période de grâce avant que les frais ne soient appliqués.',
      inputType: 'Nombre entier de jours (≥ 0)',
      example: '0, 20, 30',
    },
    'cards.0.fees.billing_period': {
      description: 'Fréquence de facturation des frais carte.',
      inputType: 'Lettre: M = Mensuel, A = Annuel, T = Trimestriel, S = Semestriel',
      example: 'M, A',
    },
    'cards.0.fees.registration_fee': {
      description: "Frais d'inscription / émission de la carte, prélevés une seule fois.",
      inputType: 'Montant numérique (≥ 0) dans la devise de la banque',
      example: '50, 0',
    },
    'cards.0.fees.periodic_fee': {
      description: 'Frais récurrents de la carte (par période de facturation: mensuel, annuel, etc.).',
      inputType: 'Montant numérique (≥ 0) dans la devise de la banque',
      example: '10, 0',
    },
    'cards.0.fees.replacement_fee': {
      description: 'Frais facturés lors du remplacement d’une carte (perte, casse…).',
      inputType: 'Montant numérique (≥ 0) dans la devise de la banque',
      example: '25, 0',
    },
    'cards.0.fees.pin_recalculation_fee': {
      description: 'Frais appliqués lors du recalcul ou de la réinitialisation du code PIN.',
      inputType: 'Montant numérique (≥ 0) dans la devise de la banque',
      example: '5, 0',
    },
    'cards.0.services.enabled': {
      description: 'Services à activer pour la carte (retrait, achat, e-commerce, 3DS, etc.).',
      inputType: 'Liste de services (virgules ou menu)',
      example: 'retrait, achat, e-commerce, solde, 3DS',
    },
    'cards.0.card_range.tranche_min': {
      description: 'Tranche PAN minimum (borne basse de la plage de numéros).',
      inputType: 'Nombre (entier ou décimal)',
      example: '100000',
    },
    'cards.0.card_range.tranche_max': {
      description: 'Tranche PAN maximum (borne haute de la plage).',
      inputType: 'Nombre (entier ou décimal)',
      example: '999999',
    },
  };

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
      error: () => {
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
        this.loadGoals();

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
          this._streamTextIntoMessage(
            res.decision.question || '',
            res.decision.paths || (res.decision.path ? [res.decision.path] : []),
            res.decision.menu,
            res.decision.form,
          );
        }
      },
      error: () => {
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
            this.messages.push({ role: 'agent', text: h.agent, timestamp: new Date() });
          }
          if (h.user) {
            this.messages.push({ role: 'user', text: h.user, timestamp: new Date() });
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
    this.agentService.chat(this.activeGoalId!, '.').subscribe({
      next: (res) => {
        this.progress = res.progress;
        this.currentDecision = res.decision;
        if (res.decision.type !== 'DONE' && res.decision.question) {
          this._streamTextIntoMessage(
            res.decision.question,
            res.decision.paths || (res.decision.path ? [res.decision.path] : []),
            res.decision.menu,
            res.decision.form,
          );
        }
      },
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

  // ─── Chat (streaming) ──────────────────────────────────────────────────────
  sendMessage() {
    if (!this.userInput.trim() || !this.activeGoalId || this.isTyping) return;

    const text = this.userInput.trim();
    this.userInput = '';

    this.messages.push({ role: 'user', text, timestamp: new Date() });
    this.isTyping = true;

    this.agentService.chatStream(this.activeGoalId, text).subscribe({
      next: (event: StreamEvent) => {
        if (event.type === 'meta') {
          this.progress = event.progress;
          // Create placeholder message for streaming
          if (event.decision_type !== 'DONE') {
            this.messages.push({
              role: 'agent',
              text: '',
              timestamp: new Date(),
              streaming: true,
            });
          }
        } else if (event.type === 'token') {
          // Append token to last agent message
          const last = this.messages[this.messages.length - 1];
          if (last?.role === 'agent' && last.streaming) {
            last.text += event.text;
          }
        } else if (event.type === 'done') {
          this.isTyping = false;
          this.progress = event.progress;
          this.currentDecision = event.decision;

          // Replace last message immutably so Angular detects the change (include paths so + help shows on every question)
          const lastIdx = this.messages.length - 1;
          const last = this.messages[lastIdx];
          const paths = event.decision.paths ?? (event.decision.path ? [event.decision.path] : []);
          if (last?.role === 'agent') {
            this.messages[lastIdx] = {
              ...last,
              streaming: false,
              paths: paths.length ? paths : last.paths,
              menu: event.decision.menu || null,
              form: event.decision.form || null,
            };
            this.messages = [...this.messages];
          }

          // Activate menu/form for input area
          this.activeMenu = event.decision.menu || null;
          this.activeForm = event.decision.form || null;
          if (this.activeForm) {
            this.formValues = {};
            for (const f of this.activeForm.fields) {
              this.formValues[f.path] = '';
            }
            for (const d of (this.activeForm.defaults || [])) {
              this.formValues[d.path] = d.value;
            }
          }

          if (event.decision.type === 'DONE') {
            this.activeMenu = null;
            this.activeForm = null;
            this.messages.push({
              role: 'agent',
              text: this.translate.instant('agent.allComplete'),
              timestamp: new Date(),
            });
            this.loadGoals();
          }

          setTimeout(() => this.messageInput?.nativeElement?.focus(), 100);
        }
      },
      error: () => {
        this.isTyping = false;
        this.messages.push({
          role: 'system',
          text: this.translate.instant('agent.errorChat'),
          timestamp: new Date(),
        });
      },
    });
  }

  // ─── Internal: animate text into a new message bubble ──────────────────────
  private _streamTextIntoMessage(
    text: string,
    paths: string[] = [],
    menu?: AgentMenu | null,
    form?: AgentForm | null,
  ) {
    const msg: ChatMessage = {
      role: 'agent',
      text: '',
      timestamp: new Date(),
      paths,
      menu: menu || null,
      form: form || null,
      streaming: true,
    };
    this.messages.push(msg);

    // Set active menu/form so input area can react
    this.activeMenu = menu || null;
    this.activeForm = form || null;
    if (form) {
      this.formValues = {};
      for (const f of form.fields) {
        this.formValues[f.path] = '';
      }
      for (const d of (form.defaults || [])) {
        this.formValues[d.path] = d.value;
      }
    }

    const words = text.split(' ');
    let idx = 0;

    const tick = () => {
      if (idx >= words.length) {
        msg.streaming = false;
        return;
      }
      msg.text += (idx > 0 ? ' ' : '') + words[idx];
      idx++;
      setTimeout(tick, 40);
    };
    tick();
  }

  // ─── Menu: user clicks an option ────────────────────────────────────────────
  selectMenuOption(value: string) {
    this.userInput = value;
    this.activeMenu = null;
    this.sendMessage();
  }

  // ─── Form: user submits a multi-field form ───────────────────────────────────
  submitForm() {
    // Build comma-separated values in the same order as form.fields so backend zip(paths, parts) matches.
    // Do not filter out empty values: we must send one value per path (empty allowed) so counts match.
    const form = this.currentDecision?.form;
    const parts = form?.fields
      ? form.fields.map((f) => (this.formValues[f.path] ?? '').toString().trim())
      : Object.entries(this.formValues)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([, v]) => v.toString().trim());
    this.userInput = parts.join(', ');
    this.activeForm = null;
    this.formValues = {};
    this.sendMessage();
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

  // ─── Param help (+ button) ──────────────────────────────────────────────────
  openParamHelp(path: string): void {
    this.helpPath = path;
  }

  closeParamHelp(): void {
    this.helpPath = null;
  }

  getParamHelpTitle(path: string): string {
    if (!path) return '';
    const segment = path.split('.').slice(-1)[0] || '';
    return segment.replace(/_/g, ' ');
  }

  getHelpForPath(path: string): { description: string; inputType: string; example: string } {
    const exact = this.PARAM_HELP[path];
    if (exact) return exact;
    // Fallback by path prefix/suffix for limits, fees, etc.
    if (path.includes('limits') && path.includes('amount')) {
      return { description: 'Montant limite (plafond) pour la période et le périmètre indiqués.', inputType: 'Nombre (≥ 0)', example: '5000, 20000' };
    }
    if (path.includes('limits') && path.includes('count')) {
      return { description: 'Nombre maximum d\'opérations autorisées pour la période indiquée.', inputType: 'Entier (≥ 0)', example: '10, 50' };
    }
    if (path.includes('fees.')) {
      return { description: 'Paramètre de frais pour la carte (montant ou code selon le champ).', inputType: 'Nombre ou code', example: '50, M, 1' };
    }
    return {
      description: 'Valeur attendue pour ce champ (voir la question pour le contexte).',
      inputType: 'Texte ou nombre selon le champ',
      example: 'Saisir une valeur conforme au message d\'erreur ou à l\'exemple affiché.',
    };
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
  toggleSidebar() { this.sidebarExpanded = !this.sidebarExpanded; }
  toggleActivity() { this.activityExpanded = !this.activityExpanded; }

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
    return this.username.split(' ').map(n => n[0]).join('').toUpperCase();
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
