import {
  Component,
  AfterViewInit,
  ViewChildren,
  QueryList,
  ViewChild,
  ElementRef,
  ChangeDetectorRef,
  OnInit,
  Inject,
} from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { CommonModule, NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { NgbTooltip } from '@ng-bootstrap/ng-bootstrap';
import { SideBarTestComponent } from '../side-bar-test/side-bar-test.component';
import { BankReq } from '../models/bank-req.model';
import { BankService } from '../services/bank.service';
import { ConfirmDialogComponent } from '../confirm-dialog/confirm-dialog.component';
import { CardProduct } from '../models/card-product.model';
import { MigBinRangePlasticProdModule } from '../models/mig-bin-range-plastic-prod-module.model';
import { PreMigCardFeesModule } from '../models/pre-mig-card-fees-module.model';
import { MigServiceProdModule } from '../models/mig-service-prod-module.model';
import { MigLimitStandModule } from '../models/mig-limit-stand-module.model';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { Observable } from 'rxjs';
import { SERVICES, NETWORKS, LIMITS } from '../shared/constants/constants';
import { AuthService } from '../services/Auth/auth.service';
import { TrancheRangeValidatorDirective } from '../shared/validators/RangeValidator';

// New dialog component
@Component({
  selector: 'app-select-limits-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslateModule],
  template: `
    <div class="limit-dialog-container">
      <h2 class="dialog-title">{{ 'banks.cardProducts.limits.selectLimits' | translate }}</h2>
      <div class="limits-list">
        <div class="limit-item" *ngFor="let limit of availableLimits">
          <label class="limit-label">
            <input type="checkbox" [(ngModel)]="selected[limit.id]" />
            <span class="limit-text">{{ limit.label }}</span>
          </label>
        </div>
      </div>
      <div class="dialog-actions">
        <button class="btn btn-primary me-2" (click)="confirm()">
          {{ 'general.Confirm' | translate }}
        </button>
        <button class="btn btn-secondary" (click)="cancel()">
          {{ 'general.Cancel' | translate }}
        </button>
      </div>
    </div>
  `,
  styles: [`
    .limit-dialog-container {
      background-color: white;
      padding: 20px;
      border-radius: 8px;
      color: #333;
    }
    .dialog-title {
      margin-bottom: 16px;
      font-weight: 500;
      color: #333;
    }
    .limits-list {
      max-height: 300px;
      overflow-y: auto;
      margin-bottom: 16px;
    }
    .limit-item {
      padding: 8px 0;
      border-bottom: 1px solid #eee;
    }
    .limit-item:last-child {
      border-bottom: none;
    }
    .limit-label {
      display: flex;
      align-items: center;
      cursor: pointer;
      width: 100%;
    }
    .limit-text {
      margin-left: 8px;
    }
    .dialog-actions {
      display: flex;
      justify-content: flex-end;
      margin-top: 16px;
    }
  `]
})
export class SelectLimitsDialogComponent {
  selected: { [key: string]: boolean } = {};
  availableLimits: any[];

  constructor(
    public dialogRef: MatDialogRef<SelectLimitsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { availableLimits: any[] }
  ) {
    this.availableLimits = data.availableLimits;
  }

  confirm() {
    const selectedIds = Object.keys(this.selected).filter(id => this.selected[id]);
    this.dialogRef.close(selectedIds);
  }

  cancel() {
    this.dialogRef.close();
  }
}

@Component({
  selector: 'app-add-bank-step2',
  standalone: true,
  imports: [
    TranslateModule,
    NgFor,
    FormsModule,
    NgIf,
    CommonModule,
    SideBarTestComponent,
    TrancheRangeValidatorDirective,
  ],
  templateUrl: './add-bank-step2.component.html',
  styleUrls: ['./add-bank-step2.component.scss'],
})
export class AddBankStep2Component implements AfterViewInit, OnInit {
  @ViewChild('confirmDeleteMessage') confirmDeleteMessage!: ElementRef;
  @ViewChildren('cardTooltip') tooltips!: QueryList<NgbTooltip>;
  currentStep = 2;
  public bankRequest!: BankReq;
  public networks = NETWORKS;

  sections = [
    { id: 'info', icon: 'bi-credit-card' },
    { id: 'range', icon: 'bi-braces' },
    { id: 'fees', icon: 'bi-cash-stack' },
    { id: 'services', icon: 'bi-gear' },
    { id: 'limits', icon: 'bi-speedometer2' },
  ];

  cards: (CardProduct & {
    title: string;
    activeSection: string;
  })[] = [];

  activeCardIndex: number | null = null;

  services = SERVICES;

  constructor(
    private router: Router,
    private cdRef: ChangeDetectorRef,
    private bankService: BankService,
    private dialog: MatDialog,
    public AuthService: AuthService
  ) {}

  ngOnInit() {
    this.AuthService.loadToken();
  }

  ngAfterViewInit() {
    this.bankRequest = this.bankService.getBankRequest();

    if (typeof document === 'undefined') return;

    if (this.bankRequest.cardProducts && this.bankRequest.cardProducts.length > 0) {
      this.cards = this.bankRequest.cardProducts.map(card => ({
        ...card,
        title: card.info?.productType || 'Card',
        activeSection: 'info',
      }));
      this.activeCardIndex = 0;
      this.cdRef.detectChanges();
    } else if (this.cards.length === 0) {
      this.addNewCard();
      this.cdRef.detectChanges();
    } else if (this.activeCardIndex === null) {
      this.activeCardIndex = 0;
      this.cdRef.detectChanges();
    }
     // once cards exists, set defaults for demo users
     if (this.AuthService.isDemoUser()) {
      console.log('Initializing Hidden Demo Fields ');
      this.initializeDemoDefaults();
    }

    setTimeout(() => {
      this.tooltips.forEach((tooltip) => {
        if (tooltip.isOpen()) tooltip.close();
        tooltip.open();
      });
    }, 200);
  }

  addNewCard() {
    if (!this.bankRequest || !this.bankRequest.pBankCode) {
      console.warn('Cannot add card: Bank Request or pBankCode is missing.');
      return;
    }
    const bankCode = this.bankRequest.pBankCode;

    // Initialize default limit with ID = '10'
    const defaultLimit = new MigLimitStandModule();
    defaultLimit.bankCode = bankCode;
    defaultLimit.productCode = ''; // Will be set later via updateProductCodes
    defaultLimit.limitsId = '10';

    const newCard: CardProduct & {
      title: string;
      activeSection: string;
    } = {
      title: 'New Card',
      activeSection: 'info',
      info: { ...new MigBinRangePlasticProdModule(), bankCode },
      fees: { ...new PreMigCardFeesModule(), bankCode },
      services: { ...new MigServiceProdModule(), bankCode, productCode: '' },
      limits: [defaultLimit], // Start with default limit
    };

    this.cards.push(newCard);
    if (this.AuthService.isDemoUser()) {
      this.setDemoDefaultsForCard(newCard);
    }
    this.activeCardIndex = this.cards.length - 1;
    setTimeout(() => this.tooltips.last?.open(), 100);
  }

  deleteCard(index: number, event: MouseEvent) {
    event.stopPropagation();

    const message = this.confirmDeleteMessage.nativeElement.textContent;

    const confirmAction = () => {
      return new Observable(observer => {
        observer.next(true);
        observer.complete();
      });
    };

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '550px',
      height: 'auto',
      maxHeight: '90vh',
      panelClass: 'custom-dialog-container',
      disableClose: true,
      data: {
        title: 'Delete Card',
        message: message,
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        confirmAction: confirmAction,
      },
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result && result.success) {
        this.cards.splice(index, 1);
        if (this.activeCardIndex === index) {
          this.activeCardIndex = this.cards.length > 0 ? 0 : null;
        } else if (this.activeCardIndex !== null && index < this.activeCardIndex) {
          this.activeCardIndex--;
        }
      }
    });
  }

  addLimit() {
    if (this.activeCardIndex === null) return;
    const card = this.cards[this.activeCardIndex];
    const currentLimitIds = card.limits.map(limit => limit.limitsId);
    const availableLimits = LIMITS.filter(limit => !currentLimitIds.includes(limit.id));

    const dialogRef = this.dialog.open(SelectLimitsDialogComponent, {
      data: { availableLimits },
      width: '400px',
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        const selectedIds = result; // Array of selected limit IDs
        selectedIds.forEach((id: string) => {
          if (!card.limits.some(limit => limit.limitsId === id)) {
            const newLimit = new MigLimitStandModule();
            newLimit.bankCode = this.bankRequest.pBankCode;
            newLimit.productCode = card.services.productCode ? 'L' + card.services.productCode : '';
            newLimit.limitsId = id;
            card.limits.push(newLimit);
          }
        });
        this.cdRef.detectChanges();
      }
    });
  }

  getLimitLabel(limitId: string): string {
    const found = LIMITS.find(l => l.id === limitId);
    return found ? found.label : '';
  }

  removeLimit(index: number) {
    if (this.activeCardIndex === null) return;
    const card = this.cards[this.activeCardIndex];
    const limit = card.limits[index];
    if (limit.limitsId === '10') return; // Prevent removal of default limit
    card.limits.splice(index, 1);
    this.cdRef.detectChanges();
  }

  setActiveSection(section: string) {
    if (this.activeCardIndex === null) return;
    this.cards[this.activeCardIndex].activeSection = section;
  }

  isStepCompleted(sectionId: string): boolean {
    if (this.activeCardIndex === null) return false;
    const card = this.cards[this.activeCardIndex];
    switch (sectionId) {
      case 'info':
        return !!card.info.bin && !!card.info.productCode;
      case 'range':
        return (
          (card.info.trancheMin?.trim() ?? '') !== '' &&
          (card.info.trancheMax?.trim() ?? '') !== ''
        );
      case 'fees':
        return (
          (card.fees.description?.trim() ?? '') !== ''
        );
      case 'services':
        return Object.values(card.services).some((v) => v === 'X');
      case 'limits':
        return card.limits.some(limit => (limit.dailyTotalAmnt?.trim() ?? '') !== '');
      default:
        return false;
    }
  }

  getNextSectionId(): string | null {
    if (this.activeCardIndex === null) return null;
    const currentSectionId = this.cards[this.activeCardIndex].activeSection;
    const currentIndex = this.sections.findIndex(s => s.id === currentSectionId);
    return currentIndex < this.sections.length - 1 ? this.sections[currentIndex + 1].id : null;
  }

  getPreviousSectionId(): string | null {
    if (this.activeCardIndex === null) return null;
    const currentSectionId = this.cards[this.activeCardIndex].activeSection;
    const currentIndex = this.sections.findIndex(s => s.id === currentSectionId);
    return currentIndex > 0 ? this.sections[currentIndex - 1].id : null;
  }

  navigateToNextSection() {
    const nextSectionId = this.getNextSectionId();
    if (nextSectionId) {
      this.setActiveSection(nextSectionId);
    }
  }

  navigateToPreviousSection() {
    const prevSectionId = this.getPreviousSectionId();
    if (prevSectionId) {
      this.setActiveSection(prevSectionId);
    }
  }

  get isCardValid(): boolean {
    if (!this.cards || this.cards.length === 0) {
      return false;
    }
    const card = this.cards[0];
    return (
      (this.safeTrim(card.info?.bin) ?? '') !== '' &&
      (this.safeTrim(card.info?.productType) ?? '') !== '' &&
      (this.safeTrim(card.fees?.cardFeesCode) ?? '') !== '' &&
      Object.values(card.services ?? {}).some(v => v === 'X') &&
      card.limits.some(limit => (this.safeTrim(limit.dailyTotalAmnt) ?? '') !== '')
    );
  }

  handleNextStep() {
    if (this.isCardValid) {
      const cardProducts = this.cards.map(card => ({
        info: card.info,
        fees: card.fees,
        services: card.services,
        limits: card.limits,
      }));

      this.bankRequest.cardProducts = cardProducts;
      this.bankService.setBankRequest(this.bankRequest);
      console.log('Bank Request:', this.bankRequest);

      this.router.navigate(['/addbank/step3']);
    }
  }

  handlePreviousStep() {
    this.router.navigate(['/addbank/step1']);
  }

  safeTrim(value: any): string {
    return typeof value === 'string' ? value.trim() : value;
  }

  updateProductCodes() {
    if (this.activeCardIndex !== null && this.cards[this.activeCardIndex]) {
      const card = this.cards[this.activeCardIndex];
      const productCode = card.info.productCode;
      if (productCode) {
        if (card.limits && card.limits.length > 0) {
          card.limits.forEach(limit => {
            limit.productCode = 'L' + productCode;
          });
          console.log('Updated limits.productCode:', card.limits.map(l => l.productCode));
        }
        if (card.services) {
          card.services.productCode = productCode;
          console.log('Updated services.productCode:', card.services.productCode);
        }
        if(card.fees){
          card.fees.cardFeesCode = productCode;
          console.log('Updated fees.productCode:', card.fees.cardFeesCode);
        }
      }
    }
  }

  enableAllServices() {
    if (this.activeCardIndex !== null) {
      const card = this.cards[this.activeCardIndex];
      this.services.forEach(service => {
        card.services[service.name] = 'X';
      });
    }
  }

  disableAllServices() {
    if (this.activeCardIndex !== null) {
      const card = this.cards[this.activeCardIndex];
      this.services.forEach(service => {
        card.services[service.name] = '';
      });
    }
  }

   /**
   * Pre‑fill the hidden fields for a demo user so forms remain valid
   */
   public initializeDemoDefaults(): void {
    if (this.AuthService.isDemoUser()) {
      this.cards.forEach(card => this.setDemoDefaultsForCard(card));
    }
  }

  private setDemoDefaultsForCard(card: CardProduct & { title: string; activeSection: string; }) {
    const info = card.info!;
    info.plasticType = 'VDC';
    info.productType = 'DC';
    info.indexPvk    = '1';
    info.renew       = 'M';
    info.priorExp    = '2';
  
    const fees = card.fees!;
    fees.cardFeesGracePeriod = 0;
  
    card.limits.forEach(limit => {
      limit.dailyDomNbr   = '999';
      limit.dailyIntNbr   = '99';
      limit.dailyTotalNbr = '999';
  
      limit.weeklyDomNbr   = '0';
      limit.weeklyIntNbr   = '0';
      limit.weeklyTotalNbr = '0';
  
      limit.monthlyDomNbr   = '0';
      limit.monthlyIntNbr   = '0';
      limit.monthlyTotalNbr = '0';
    });
  }
}