import {
  Component,
  OnInit,
  AfterViewChecked,
  ViewChild,
  ChangeDetectorRef,
  AfterViewInit
} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { BankService } from '../services/bank.service';
import { BankApiService } from '../services/Bank/bank-api.service';
import { BankReq } from '../models/bank-req.model';
import { AddBankStep1Component } from '../add-bank-step1/add-bank-step1.component';
import { AddBankStep2Component } from '../add-bank-step2/add-bank-step2.component';
import { NgIf } from '@angular/common';
import { CardProduct } from '../models/card-product.model';
import { MatDialog } from '@angular/material/dialog';
import { SuccessDialogComponent, SuccessDialogData } from '../success-dialog/success-dialog.component';
import { TranslateModule } from '@ngx-translate/core';
import { AuthService } from '../services/Auth/auth.service';

@Component({
  selector: 'app-edit-bank',
  templateUrl: './edit-bank.component.html',
  standalone: true,
  imports: [AddBankStep1Component,
            AddBankStep2Component,
            NgIf,
            TranslateModule],
  styleUrls: [
    './edit-bank.component.scss',
    '../add-bank-step1/add-bank-step1.component.scss',
    '../add-bank-step2/add-bank-step2.component.scss',
  ],
})
export class EditBankComponent implements OnInit, AfterViewChecked {
  @ViewChild(AddBankStep1Component) step1!: AddBankStep1Component;
  @ViewChild(AddBankStep2Component) step2!: AddBankStep2Component;

  loading = true;
  error: string | null = null;
  ready = false;
  private populated = false;
  private submitStart = 0;
  
  isSubmitting = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private bankApi: BankApiService,
    private bankService: BankService,
    private cd: ChangeDetectorRef,
    private dialog: MatDialog,
    private AuthService: AuthService,
  ) {}

  ngOnInit(): void {
    this.loadBankData();
  }

 

  private loadBankData(): void {
    const code = this.route.snapshot.paramMap.get('bankCode');
    if (!code) {
      this.error = 'Aucun code de banque fourni.';
      this.loading = false;
      return;
    }
  
    this.bankApi.getBankByCode(code).subscribe({
      next: bank => {
        const rawCards = (bank.cardProducts as any[]) || [];
  
        const nestedCards: CardProduct[] = rawCards.map(flatCard => ({
          info: {
            bankCode:     bank.pBankCode,
            bin:          flatCard.bin,
            description:  flatCard.description,
            expiration:   flatCard.expiration,
            trancheMin:   flatCard.trancheMin,
            trancheMax:   flatCard.trancheMax,
            indexPvk:     flatCard.indexPvk,
            network:      flatCard.network,
            plasticType:  flatCard.plasticType,
            priorExp:     flatCard.priorExp,
            productCode:  flatCard.productCode,
            productType:  flatCard.productType,
            renew:        flatCard.renew,
            serviceCode:  flatCard.serviceCode,
          } as any,
          fees:     flatCard.fees,
          services: flatCard.services,
          limits:   flatCard.limits || [],
        }));
  
        const bankReq: BankReq = {
          pBusinessDate: bank.pBusinessDate,
          pBankCode:     bank.pBankCode,
          pBankWording:  bank.pBankWording,
          pCountryCode:  bank.pCountryCode,
          pCurrencyCode: bank.pCurrencyCode,
          p_action_flag: bank.p_action_flag || '2',
          cardProducts:  nestedCards,
          branches:      bank.branches || [],
          ressources:    bank.ressources || [],
        };
  
        this.bankService.setBankRequest(bankReq);
        this.loading = false;
        this.ready   = true;
      },
      error: err => {
        console.error('Erreur chargement banque :', err);
        this.error   = 'Impossible de charger la banque.';
        this.loading = false;
      }
    });
  }
  
  ngAfterViewChecked(): void {
    if (this.ready && !this.populated && this.step1 && this.step2 && !this.step1.isLoadingResources) {
      this.populateChildForms();
      this.populated = true;
      this.cd.detectChanges();
    }
    // Immediately after “populateChildForms” has run (so step2 now exists),
    // you can call initializeDemoDefaults() if it’s a demo user:
    if (this.ready && this.step2 && this.AuthService.isDemoUser() ) {
      this.step2.initializeDemoDefaults();
      console.log("Initialized Fields for Demo User");
    }
  }

  private populateChildForms(): void {
    const req = this.bankService.getBankRequest();

    this.step1.bankData = {
      pBankWording:  req.pBankWording,
      pCountryCode:  req.pCountryCode,
      pCurrencyCode: req.pCurrencyCode,
      pBankCode:     req.pBankCode,
    };
    this.step1.agencies  = [...req.branches];

    this.step1.selectedResources = {};
    req.ressources?.forEach(savedRes => {
      const match = this.step1.availableResources.find(
        ar => ar.abrv_wording === savedRes.resourceWording
      );
      if (match) {
        this.step1.selectedResources[match.resource_id] = true;
      }
    });

    this.step2.bankRequest = req;
    this.step2.cards = req.cardProducts.map(card => ({
      title:         card.info?.productType  || 'Card',
      activeSection: 'info',
      info:     card.info,
      fees:     card.fees,
      services: card.services,
      limits:   card.limits,
    }));
    this.step2.activeCardIndex = this.step2.cards.length > 0 ? 0 : null;
  }

  private syncRequestFromForms(): BankReq | null {
    const req = this.bankService.getBankRequest();
    if (!req) { return null; }

    req.pBankWording  = this.step1.bankData.pBankWording;
    req.pCountryCode  = this.step1.bankData.pCountryCode;
    req.pCurrencyCode = this.step1.bankData.pCurrencyCode;
    req.pBankCode     = this.step1.bankData.pBankCode;
    req.branches      = [...this.step1.agencies];

    req.ressources = this.step1.availableResources
      .filter(res => this.step1.selectedResources[res.resource_id])
      .map(res => ({
        bankCode: req.pBankCode,
        resourceId: res.resource_id,
        resourceWording: res.abrv_wording
      }));

    req.cardProducts = this.step2.cards.map(card => ({
      info:     card.info,
      fees:     card.fees,
      services: card.services,
      limits:   card.limits
    }));

    this.bankService.setBankRequest(req);
    return req;
  }

  onSubmit(): void {
    this.submitStart = Date.now();
    const req = this.syncRequestFromForms();
    if (!req) {
      this.error = 'Données introuvables.';
      return;
    }
    
    this.isSubmitting = true;
    this.bankApi.editBank(req).subscribe({
      next: () => {
        this.isSubmitting = false;
        const elapsedMs = Date.now() - this.submitStart;
        const seconds = Math.floor(elapsedMs / 1000);
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        const elapsedStr = minutes > 0
          ? `${minutes} min ${remainingSeconds} s`
          : `${remainingSeconds} s`;
          
        const dialogRef = this.dialog.open<SuccessDialogComponent, SuccessDialogData>(
          SuccessDialogComponent,
          {
            data: { 
              message: 'La mise à jour a bien été effectuée !',
              elapsed: elapsedStr
            },
            disableClose: true
          }
        );
        dialogRef.afterClosed().subscribe(() => {
          this.router.navigate(['/banks']);
        });
      },
      error: err => {
        console.error('MàJ échouée :', err);
        this.error = 'La mise à jour a échoué.';
        this.isSubmitting = false;
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/banks']);
  }
}