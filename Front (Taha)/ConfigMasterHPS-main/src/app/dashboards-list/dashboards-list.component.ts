import { CommonModule, isPlatformBrowser, NgClass, NgIf } from '@angular/common';
import { Component, OnInit, OnDestroy, PLATFORM_ID, Inject, Output, EventEmitter, AfterViewInit, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule, RouterOutlet } from '@angular/router';
import { AuthService } from '../services/Auth/auth.service';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { provideCharts, withDefaultRegisterables, BaseChartDirective } from 'ng2-charts';
import { Chart, ChartData, ChartOptions, registerables } from 'chart.js';
import { Subscription, catchError, forkJoin,of } from 'rxjs';

import { Patch } from '../models/patch.model';
import { PatchArchetService } from '../services/Patch_Architecture/patch-service.service';
import { BankApiService } from '../services/Bank/bank-api.service';
import { BankReq } from '../models/bank-req.model';
import { Architecte } from '../models/architecte.model';
import { Transaction } from '../models/transaction.model';
import { DashboardService } from '../services/Dashboard/dashboard-service.service'; 
import { Network, DataSet, Node, Edge } from 'vis-network/standalone';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { ContextBank } from '../models/context-bank.model';

// Register chart.js components and the datalabels plugin
Chart.register(...registerables, ChartDataLabels);

@Component({
  selector: 'app-dashboards-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    NgClass,
    NgIf,
    TranslateModule,
    BaseChartDirective,
    RouterOutlet,
    RouterModule,
  ],
  templateUrl: './dashboards-list.component.html',
  styleUrls: ['./dashboards-list.component.scss'],
  providers: [provideCharts(withDefaultRegisterables())],
})
export class DashboardsListComponent implements OnInit, OnDestroy, AfterViewInit {
  // UI state
  pageTitle = 'dashboard.title';
  username = 'John Doe';
  sidebarExpanded = false;
  today: Date = new Date();
  activityExpanded = false;

  // Patches
  patches: Patch[] = [];
  isLoadingPatches = true;
  patchesError: string | null = null;
  private patchesSub?: Subscription;

  // Banks
  banks: BankReq[] = [];
  isLoadingBanks = true;
  banksError: string | null = null;
  selectedBankCode: string | null = null;
  private banksSub?: Subscription;
  selectedBankWording!: string;

  // Architecture nodes
  archNode1: Architecte[] = [];
  archNode2: Architecte[] = [];
  isLoadingNodes = false;
  node1Error: string | null = null;
  node2Error: string | null = null;
  private nodesSub?: Subscription;
  private network1?: Network;
  private network2?: Network;
  private shouldRenderDiagrams = false;

  // Context-related properties
bankContext: ContextBank | null = null;
isLoadingContext: boolean = false;
contextError: string | null = null;
contextFetched: boolean = false;


  // Transactions
  selectedTransactionDate: string | null = null;
  transactions: Transaction[] = [];
  isLoadingTransactions = false;
  transactionsError: string | null = null;
  // 1) New chart properties
  public transactionChartData?: ChartData<'pie', number[], string | string[]>;
  public transactionChartOptions: ChartOptions<'pie'> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'left' },
    tooltip: { enabled: true },
    datalabels: {
      color: '#fff', // White text for visibility
      borderRadius: 3, // Rounded corners for the label background
      padding: 4, // Padding inside the label background
      formatter: (value: number, context: any) => {
        return value > 0 ? `${value}%` : ''; // Only show non-zero values
      },
      font: {
        weight: 'bold',
        size: 12,
      },
      anchor: 'center',
      align: 'center',
    },
  },
};

  @Output() bankSelected = new EventEmitter<string>();
  @ViewChild('transactionPieChart') chart?: BaseChartDirective;

  constructor(
    public authService: AuthService,
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object,
    private patchArchetService: PatchArchetService,
    private bankService: BankApiService,
    private dashboardService: DashboardService,
    private translate: TranslateService
  ) {}

  toggleActivity() {
    this.activityExpanded = !this.activityExpanded;
  }

  ngAfterViewInit(): void {
    if (this.shouldRenderDiagrams) {
      this.renderDiagrams();
    }
  }

  ngOnInit(): void {
    this.setUsername();
    this.loadPatches();
    this.loadBanks();
    
  }

  private setUsername(): void {
    const userInfo = this.authService.getUserInfo();
    if (userInfo?.email) {
      this.username = userInfo.email.split('@')[0];
    } else if (this.authService.loggedUser) {
      this.username = this.authService.loggedUser.split('@')[0];
    }
  }

  private loadPatches(): void {
    this.isLoadingPatches = true;
    this.patchesError = null;

    this.patchesSub = this.patchArchetService.getAllPatches().subscribe({
      next: data => {
        this.patches = data;
        this.isLoadingPatches = false;
      },
      error: err => {
        console.error(err);
        const key = 'dashboard.patches.errorLoading';
        const msg = this.translate.instant(key);
        this.patchesError = msg === key
          ? 'Failed to load patches. Please try again later.'
          : msg;
        this.isLoadingPatches = false;
      }
    });
  }

  private loadBanks(): void {
    this.isLoadingBanks = true;
    this.banksError = null;

    this.banksSub = this.bankService.getAllBanks().subscribe({
      next: list => {
        this.banks = list;
        this.isLoadingBanks = false;
      },
      error: err => {
        console.error(err);
        this.banksError = 'Failed to load banks. Please try again later.';
        this.isLoadingBanks = false;
      }
    });
  }

  onBankSelect(): void {
    if (this.selectedBankCode) {
      this.bankSelected.emit(this.selectedBankCode);
      const selectedBank = this.banks.find(bank => bank.pBankCode === this.selectedBankCode);
      this.selectedBankWording = selectedBank ? selectedBank.pBankWording : 'Unknown Bank';
      console.log("Selected Bank Code:", this.selectedBankCode, "Selected Bank Wording:", this.selectedBankWording);
      this.loadArchitectureNodes(this.selectedBankCode);
      this.fetchBankContext();
      if (this.selectedTransactionDate) {
        this.loadTransactions();
      }
      this.resetContextData();
    }
  }


  toggleSidebar(): void {
    this.sidebarExpanded = !this.sidebarExpanded;
  }

  logout(): void {
    this.authService.logout();
  }

  getUserInitials(): string {
    if (!this.username) return '??';
    const parts = this.username.split(/[.\-_@ ]+/);
    if (parts.length > 1) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return parts[0].substring(0, 2).toUpperCase();
  }

  private loadArchitectureNodes(code: string) {
    this.isLoadingNodes = true;
  
    // Reset both data and errors before fetching
    this.archNode1 = [];
    this.archNode2 = [];
    this.node1Error = null;
    this.node2Error = null;
    this.shouldRenderDiagrams = false;
  
    this.nodesSub = forkJoin({
      node1: this.patchArchetService.getArchitectureNode1(code).pipe(
        catchError(err => {
          // If Node 1 fails, store the error string and return an empty array
          this.node1Error = `Failed to load Node 1: ${err.message || err}`;
          return of<Architecte[]>([]);
        })
      ),
      node2: this.patchArchetService.getArchitectureNode2(code).pipe(
        catchError(err => {
          // If Node 2 fails, store the error string and return an empty array
          this.node2Error = `Failed to load Node 2: ${err.message || err}`;
          return of<Architecte[]>([]);
        })
      )
    }).subscribe({
      next: ({ node1, node2 }) => {
        // Assign whatever came back (possibly empty arrays on error)
        this.archNode1 = Array.isArray(node1) ? node1 : [];
        this.archNode2 = Array.isArray(node2) ? node2 : [];
  
        this.isLoadingNodes = false;
  
        // Only render diagrams for whichever node(s) actually have data
        // If either array has at least one item, we attempt rendering
        if ((this.archNode1.length > 0 || this.archNode2.length > 0) &&
            isPlatformBrowser(this.platformId)) {
          this.shouldRenderDiagrams = true;
          // Allow Angular to paint the <div id="networkDiagramX"> first,
          // then call renderDiagrams() in a setTimeout(..., 0).
          setTimeout(() => this.renderDiagrams(), 0);
        }
      },
      error: (err) => {
        // In practice, forkJoin will not call this if we catch errors above,
        // but it’s good to have a fallback.
        console.error('Unexpected error in forkJoin', err);
        this.node1Error = this.node1Error || 'Failed to load Node 1.';
        this.node2Error = this.node2Error || 'Failed to load Node 2.';
        this.isLoadingNodes = false;
      }
    });
  }

  private renderDiagrams(): void {
    if (!isPlatformBrowser(this.platformId)) return;
  
    const options = {
      nodes: { font: { size: 14, color: '#000' }, borderWidth: 2 },
      edges: {
        color: '#00008B',
        width: 2,
        length: 200,
        font: { size: 12, color: '#000', align: 'top', strokeWidth: 0 },
        arrows: { // Default global arrow configuration
          to: { enabled: true, scaleFactor: 1.5, type: 'arrow' },
          from: { enabled: true, scaleFactor: 1.5, type: 'arrow' }
        }
      },
      physics: {
        enabled: false,
        stabilization: true,
        solver: 'barnesHut',
        barnesHut: {
          gravitationalConstant: -2000,
          centralGravity: 0.3,
          springLength: 200,
          springConstant: 0.04,
          damping: 0.09,
          avoidOverlap: 1
        }
      }
    };
  
    // ─── Render Node 1 ───
    if (this.archNode1.length > 0) {
      const container1 = document.getElementById('networkDiagram1');
      if (container1) {
        if (this.network1) {
          this.network1.destroy();
        }
        const nodes1 = new DataSet<Node>([
          { id: 'bank1', label: this.selectedBankWording, color: '#4682B4', shape: 'circle', size: 40 }
        ]);
        const edges1 = new DataSet<Edge>();
  
        this.archNode1.forEach((node, index) => {
          const wordingId = `wording1_${index}`;
          const wordingLabel = `${node.libelle}\n${node.resourceId}`;
          nodes1.add({
            id: wordingId,
            label: wordingLabel,
            color: '#FFD700',
            shape: 'ellipse',
            size: 40
          });
  
          // Correctly define the source and target of the edge based on prisConnectMode
          const from = node.prisConnectMode === 'M' ? wordingId : 'bank1';
          const to = node.prisConnectMode === 'M' ? 'bank1' : wordingId;
          const label = `( ${node.resourceLive}, ${node.prisProcessingStep} )`;
  
          // Always point the arrow towards the 'to' node of the defined edge
          edges1.add({ from, to, label, font: { align: 'top' }, arrows: 'to' }); // MODIFIED LINE
        });
  
        this.network1 = new Network(container1, { nodes: nodes1, edges: edges1 }, options);
      }
    }
  
    // ─── Render Node 2 ───
    if (this.archNode2.length > 0) {
      const container2 = document.getElementById('networkDiagram2');
      if (container2) {
        if (this.network2) {
          this.network2.destroy();
        }
        const nodes2 = new DataSet<Node>([
          { id: 'bank2', label: this.selectedBankWording, color: '#4682B4', shape: 'circle', size: 40 }
        ]);
        const edges2 = new DataSet<Edge>();
  
        this.archNode2.forEach((node, index) => {
          const wordingId = `wording2_${index}`;
          const wordingLabel = `${node.libelle}\n${node.resourceId}`;
          nodes2.add({
            id: wordingId,
            label: wordingLabel,
            color: '#FFD700',
            shape: 'ellipse',
            size: 40
          });
  
          // Correctly define the source and target of the edge based on prisConnectMode
          const from = node.prisConnectMode === 'M' ? wordingId : 'bank2';
          const to = node.prisConnectMode === 'M' ? 'bank2' : wordingId;
          const label = `( ${node.resourceLive},  ${node.prisProcessingStep} )`;
  
          // Always point the arrow towards the 'to' node of the defined edge
          edges2.add({ from, to, label, font: { align: 'top' }, arrows: 'to' }); // MODIFIED LINE
        });
  
        this.network2 = new Network(container2, { nodes: nodes2, edges: edges2 }, options);
      }
    }
  }
  

  onDateChange(newDate: string): void {
    this.selectedTransactionDate = newDate; // Keep as YYYY-MM-DD for the input
    if (this.selectedBankCode && this.selectedTransactionDate) {
      this.loadTransactions();
    }
  }

  public formatTo_ddMMyyyy(isoDate: string | null): string {
    if (!isoDate) {
      return '';
    }
    const [year, month, day] = isoDate.split('-');
    return `${day}-${month}-${year}`;
  }

private loadTransactions(): void {
  if (!this.selectedBankCode || !this.selectedTransactionDate) {
    return;
  }
  this.isLoadingTransactions = true;
  this.transactionsError = null;

  const formattedDate = this.formatTo_ddMMyyyy(this.selectedTransactionDate);

  this.dashboardService.getTransactions(this.selectedBankCode, formattedDate)
    .subscribe({
      next: (transactions) => {
        this.transactions = transactions;
        this.isLoadingTransactions = false;

        if (this.transactions.length > 0) {
        const t = this.transactions[0];

       // 1. Normalize strings:
    const approvedStr       = (t.perApproved                || '').replace('%','').trim();
    const cancelAprStr      = (t.perCancellationApproved   || '').replace(',','.').replace('%','').trim();
    const cancelRejStr      = (t.perCancellationRejected   || '').replace(',','.').replace('%','').trim();
    const declinedTechStr   = (t.perDeclinedTech           || '').replace(',','.').replace('%','').trim();
    const declinedFoncStr   = (t.perDeclinedFonc           || '').replace(',','.').replace('%','').trim();

    // 2. Parse floats (fallback to 0 if still NaN):
    const approved           = isNaN(parseFloat(approvedStr))         ? 0 : parseFloat(approvedStr);
    const cancelApproved     = isNaN(parseFloat(cancelAprStr))        ? 0 : parseFloat(cancelAprStr);
    const cancelRejected     = isNaN(parseFloat(cancelRejStr))        ? 0 : parseFloat(cancelRejStr);
    const declinedTech       = isNaN(parseFloat(declinedTechStr))     ? 0 : parseFloat(declinedTechStr);
    const declinedFonc       = isNaN(parseFloat(declinedFoncStr))     ? 0 : parseFloat(declinedFoncStr);

    console.log({ approved, cancelApproved, cancelRejected, declinedTech, declinedFonc });
  // 3) Build your pieChartData exactly as before
  this.transactionChartData = {
    labels: [
      this.translate.instant('dashboard.transactions.perApproved'),
      this.translate.instant('dashboard.transactions.perCancellationApproved'),
      this.translate.instant('dashboard.transactions.perCancellationRejected'),
      this.translate.instant('dashboard.transactions.perDeclinedTech'),
      this.translate.instant('dashboard.transactions.perDeclinedFonc'),
    ],
    datasets: [{
      data: [
        approved,
        cancelApproved,
        cancelRejected,
        declinedTech,
        declinedFonc
      ],
      backgroundColor: [
        '#4CAF50', '#FFC107', '#FF5722', '#03A9F4', '#9C27B0'
      ],
      type:'pie',
      hoverBorderColor: '#fff',
      
    }]
  };
}

      },
      error: (err) => {
        console.error('Error loading transactions', err);
        this.transactionsError = 'Failed to load transactions. Please try again later.';
        this.isLoadingTransactions = false;
      }
    });
}

  ngOnDestroy(): void {
    this.patchesSub?.unsubscribe();
    this.banksSub?.unsubscribe();
    this.nodesSub?.unsubscribe();
    if (this.network1) {
      this.network1.destroy();
    }
    if (this.network2) {
      this.network2.destroy();
    }
  }

  // Add this method to your component class:
fetchBankContext(): void {
  if (!this.selectedBankCode) {
    return;
  }

  this.isLoadingContext = true;
  this.contextError = null;
  this.bankContext = null;

  this.patchArchetService.getContextBank(this.selectedBankCode).subscribe({
    next: (response) => {
      this.isLoadingContext = false;
      this.contextFetched = true;
      
      if (typeof response === 'string') {
        // It's an error message (404 case)
        this.contextError = response;
        this.bankContext = null;
      } else {
        // It's a ContextBank object
        this.bankContext = response;
        this.contextError = null;
      }
    },
    error: (error) => {
      this.isLoadingContext = false;
      this.contextFetched = true;
      this.contextError = 'Une erreur est survenue lors du chargement du contexte.';
      this.bankContext = null;
      console.error('Error fetching bank context:', error);
    }
  });
}

// Add this helper method:
private resetContextData(): void {
  this.bankContext = null;
  this.isLoadingContext = false;
  this.contextError = null;
  this.contextFetched = false;
}
}