import { DatePipe, NgClass, NgFor, NgIf } from '@angular/common';
import { Component, HostListener, OnDestroy, OnInit } from '@angular/core'; // Import OnDestroy
import { Router, RouterModule } from '@angular/router';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { AuthService } from '../services/Auth/auth.service';
import { BankApiService } from '../services/Bank/bank-api.service';
import { BankWithUI } from '../models/bank-req.model';
import { FormsModule } from '@angular/forms';
import { forkJoin, Subscription, timer } from 'rxjs'; // Import Subscription and timer
import {Country} from '../models/country.model'
import { Currency } from '../models/currency.model';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '../confirm-dialog/confirm-dialog.component';
import { SuccessDialogComponent } from '../success-dialog/success-dialog.component';
import { BankService } from '../services/bank.service';

@Component({
  selector: 'app-banks-list',
  templateUrl: './banks-list.component.html',
  standalone: true,
  imports: [
    TranslateModule,
    NgClass,
    NgFor,
    NgIf,
    DatePipe,
    RouterModule,
    FormsModule,
  ],
  styleUrls: ['./banks-list.component.scss'],
})
export class BanksListComponent implements OnInit, OnDestroy { // Implement OnDestroy
  sidebarExpanded = false;
  isMobile = false;
  username = '';
  banks: BankWithUI[] = [];
  activityExpanded = false;
  isLoading = true;
  errorMessage: string | null = null;
  searchTerm: string = '';
  countries: Country[] = [];
  currencies: Currency[] = [];
  private deleteStart: number = 0;

  // --- NEW: Add success message property ---
  successMessage: string | null = null;
  private successMessageTimerSubscription: Subscription | null = null; // To manage timeout

  constructor(
    private router: Router,
    private translate: TranslateService,
    private authService: AuthService,
    private bankApiService: BankApiService,
    private dialog : MatDialog,
    private bankService : BankService
  ) {
    this.errorMessage=null;}

    toggleActivity() {
      this.activityExpanded = !this.activityExpanded;
    }
    
  ngOnInit() {
    this.isLoading = true;
    this.errorMessage = null;
    this.checkScreenSize();
    this.getUserInfo();
    this.loadBanks();
    this.bankService.initializeBankRequest();
  }

  // --- Implement OnDestroy ---
  ngOnDestroy(): void {
    // Unsubscribe from the timer if the component is destroyed
    this.successMessageTimerSubscription?.unsubscribe();
  }

  get filteredBanks(): BankWithUI[] {
    if (!this.searchTerm) {
      return this.banks;
    }
    return this.banks.filter((bank) =>
      bank.pBankWording
        ?.toLowerCase()
        .includes(this.searchTerm.toLowerCase())
    );
  }

  loadBanks() {
    this.isLoading = true;
    this.errorMessage = null;
    // Clear success message when reloading
    this.successMessage = null;
    this.successMessageTimerSubscription?.unsubscribe();

    forkJoin([
      this.bankApiService.getAllBanks(),
      this.bankApiService.getAllCountries(),
      this.bankApiService.getAllCurrencies()
    ]).subscribe({
      next: ([banks, countries, currencies]) => {
        this.errorMessage=null;
        console.log('Banks loaded successfully :', banks);

        this.countries=countries;
        this.currencies=currencies;
        this.banks = banks.map(bank => {
          // find the matching country & currency
          const country = this.countries.find(c => c.countryCode === bank.pCountryCode);
          const currency = this.currencies.find(cu => cu.currencyCode === bank.pCurrencyCode);
  
          return {
            ...bank,
            isExpanded: false,
            accountCount: bank.cardProducts?.length || 0,
            lastUpdated: bank.pBusinessDate,
            // attach them so template can do bank.country.wording, etc.
            country,
            currency
          };
        });
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading banks:', err);
        this.errorMessage = 'Failed to load banks. Please try again later.';
        this.isLoading = false;
        if (err.status === 401) {
          this.authService.logout();
          this.router.navigate(['/login']);
        }
      },
    });
  }

  deleteBank(codeBank: string): void {
    const bankToDelete = this.banks.find(bank => bank.pBankCode === codeBank);
    const bankName = bankToDelete?.pBankWording || 'Bank';

      // 1. record when they clicked
    this.deleteStart = Date.now();

    const confirmAction = () => {
      return this.bankApiService.deleteBank(codeBank);
    };

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '550px',
      height: 'auto',
      maxHeight: '90vh',
      panelClass: 'custom-dialog-container',
      disableClose: true,
      data: {
        title: this.translate.instant('banks.confirmDeleteTitle'),
        message: this.translate.instant('banks.confirmDelete', { bankName: bankName }),
        confirmButtonText: this.translate.instant('common.delete'),
        cancelButtonText: this.translate.instant('common.cancel'),
        confirmAction: confirmAction
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result && result.success) {
        // Update the banks list (client-side)
        this.banks = this.banks.filter((bank) => bank.pBankCode !== codeBank);
        // now open success dialog with elapsed
          const elapsedMs = Date.now() - this.deleteStart;
          const secs = Math.floor(elapsedMs / 1000);
          const mins = Math.floor(secs / 60);
          const secR = secs % 60;
          const elapsedStr = mins > 0 ? `${mins} min ${secR} s` : `${secR} s`;

        // Open SuccessDialogComponent
        const successDialogRef = this.dialog.open(SuccessDialogComponent, {
          width: '400px',
          data: {
            message: this.translate.instant('banks.deleteSuccess', { bankName: bankName }),
            elapsed: elapsedStr
          }
        });

        // Navigate to /banks after dialog is closed
        successDialogRef.afterClosed().subscribe(() => {
          this.router.navigate(['/banks']);
        });

        console.log("Deleted Bank");
      }
    });
  }

  // Update trackBy
  trackById(index: number, bank: BankWithUI): string {
    return bank.pBankCode;
  }

  // Other methods remain the same...
  viewDetails(codeBank: string): void {
    this.router.navigate(['/banks/details', codeBank]);
  }

  modifyBank(codeBank: string): void {
    this.router.navigate(['/banks/edit', codeBank]);
  }

  @HostListener('window:resize', ['$event'])
  onResize() {
    if (typeof window !== 'undefined') {
      this.checkScreenSize();
    }
  }

  checkScreenSize() {
    if (typeof window !== 'undefined') {
      this.isMobile = window.innerWidth < 768;
      if (this.isMobile) {
        this.sidebarExpanded = false;
      }
    }
  }

  toggleSidebar() {
    this.sidebarExpanded = !this.sidebarExpanded;
    if (this.isMobile) {
      if (this.sidebarExpanded) {
        this.addOverlay();
      } else {
        this.removeOverlay();
      }
    }
  }

  addOverlay() {
    if (!document.querySelector('.sidebar-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay active';
        overlay.addEventListener('click', () => this.toggleSidebar());
        document.body.appendChild(overlay);
    }
  }

  removeOverlay() {
     const overlay = document.querySelector('.sidebar-overlay');
     if (overlay) {
        document.body.removeChild(overlay);
     }
  }

  getUserInfo() {
    if (this.authService.isFullUser()) {
      this.username = 'Full Profile';
    } else if (this.authService.isDemoUser()) {
      this.username = 'Demo Profile';
    } else {
      this.username = 'User'; // Fallback
    }
  }

  getUserInitials(): string {
    return this.username
      .split(' ')
      .map((name) => name[0])
      .join('')
      .toUpperCase();
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  toggleBankDetails(bank: BankWithUI): void {
    bank.isExpanded = !bank.isExpanded;
  }
}