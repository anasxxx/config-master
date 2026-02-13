import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { MatDialog } from '@angular/material/dialog';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SideBarTestComponent } from '../side-bar-test/side-bar-test.component';
import { BankReq } from '../models/bank-req.model';
import { BankService } from '../services/bank.service';
import { MigServiceProdModule } from '../models/mig-service-prod-module.model';
import { CardProduct } from '../models/card-product.model';
import { BankApiService } from '../services/Bank/bank-api.service';
import { AuthService } from '../services/Auth/auth.service';
import { Country } from '../models/country.model';
import { Currency } from '../models/currency.model';
import { forkJoin } from 'rxjs';
import { SuccessDialogComponent } from '../success-dialog/success-dialog.component';
import { SERVICES } from '../shared/constants/constants';

@Component({
  selector: 'app-add-bank-step3',
  standalone: true,
  imports: [TranslateModule, CommonModule, FormsModule, SideBarTestComponent],
  templateUrl: './add-bank-step3.component.html',
  styleUrls: ['./add-bank-step3.component.scss'],
})
export class AddBankStep3Component implements OnInit {
  countries: Country[] = [];
  currencies: Currency[] = [];
  isLoading = true;
  loadError: string | null = null;
  currentStep = 3;
  bankRequest: BankReq;
  isSubmitting = false;
  errorMessage: string | null = null;
  successMessage: string | null = null;

  // Bank data for display
  bankData = {
    name: '',
    country: '',
    currency: '',
  };

  selectedAgencies: string[] = [];
  cards: CardProduct[] = [];
  resources: string[] = [];

  // Service labels based on MigServiceProdModule properties
  readonly serviceLabels: { [name: string]: string } =
  Object.fromEntries(SERVICES.map(s => [s.name, s.label]));

  private submitStart: number = 0;

  constructor(
    private router: Router,
    private bankService: BankService,
    private BankApiService: BankApiService,
    private authService: AuthService,
    private datePipe: DatePipe,
    private dialog: MatDialog
  ) {
    this.bankRequest = this.bankService.getBankRequest();
  }

  ngOnInit() {
    this.loadReferenceData();
    // Map BankReq data to component properties
    this.bankData = {
      name: this.bankRequest.pBankWording,
      country: this.bankRequest.pCountryCode,
      currency: this.bankRequest.pCurrencyCode,
    };
    this.selectedAgencies = this.bankRequest.branches.map(
      (branch) => branch.branchWording
    );
    this.cards = this.bankRequest.cardProducts;
    this.resources = this.bankRequest.ressources.map(
      (resource) => resource.resourceWording
    );
  }

  getActiveServices(services: MigServiceProdModule): string[] {
    return Object.keys(services).filter((key) => {
      if (key === 'bankCode' || key === 'productCode') {
        return false;
      }
      const value = services[key];
      if (!value) {
        return false;
      }
      if (typeof value === 'string') {
        return value.trim() !== '';
      }
      return !!value;
    });
  }

  getServiceLabel(service: string): string {
    return this.serviceLabels[service] || service;
  }

  submitConfiguration() {
    this.submitStart = Date.now(); 
    this.isSubmitting = true;
    this.errorMessage = null;
    this.bankRequest.p_action_flag = '1';
  
    this.BankApiService.addBank(this.bankRequest).subscribe({
      next: () => {
        console.log('Bank created successfully');
        this.bankService.setBankRequest(new BankReq());
        this.isSubmitting = false;

        const elapsedMs = Date.now() - this.submitStart;
        const seconds = Math.floor(elapsedMs / 1000);
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        const elapsedStr = minutes > 0
          ? `${minutes} min ${remainingSeconds} s`
          : `${remainingSeconds} s`;
  
        const dialogRef = this.dialog.open(SuccessDialogComponent, {
          width: '400px',
          data: { 
            message: 'Bank created successfully!',
            elapsed: elapsedStr
          }
        });
        dialogRef.afterClosed().subscribe(() => {
          this.router.navigate(['/banks']);
        });
      },
      error: (err) => {
        this.isSubmitting = false;
        console.error('Error creating bank:', err);
  
        if (err.status === 401) {
          this.authService.logout();
          this.router.navigate(['/login']);
        } else {
          this.errorMessage = err.error?.message 
            || 'Failed to create bank. Please try again.';
        }
      }
    });
  }
  
  handlePreviousStep() {
    this.router.navigate(['/addbank/step2']);
  }

  public loadReferenceData() {
    forkJoin({
      countries: this.BankApiService.getAllCountries(),
      currencies: this.BankApiService.getAllCurrencies(),
    }).subscribe({
      next: ({ countries, currencies }) => {
        this.countries = countries;
        this.currencies = currencies;
        this.initializeDisplayData();
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading reference data:', err);
        this.loadError = 'Failed to load reference data';
        this.isLoading = false;
        this.initializeDisplayData();
      },
    });
  }

  private initializeDisplayData() {
    const country = this.countries.find(
      (c) => c.countryCode === this.bankRequest.pCountryCode
    );
    const currency = this.currencies.find(
      (c) => c.currencyCode === this.bankRequest.pCurrencyCode
    );

    this.bankData = {
      name: this.bankRequest.pBankWording,
      country: country?.abrvWording || this.bankRequest.pCountryCode,
      currency: currency?.currencyAlpha || this.bankRequest.pCurrencyCode,
    };

    this.selectedAgencies = this.bankRequest.branches.map(
      (branch) => branch.branchWording
    );
    this.cards = this.bankRequest.cardProducts;
    this.resources = this.bankRequest.ressources.map(
      (resource) => resource.resourceWording
    );
  }
}