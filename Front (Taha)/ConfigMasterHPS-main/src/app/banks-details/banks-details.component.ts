import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { Router, ActivatedRoute } from '@angular/router';
import { BankReq } from '../models/bank-req.model';
import { CardProduct } from '../models/card-product.model';
import { BankApiService } from '../services/Bank/bank-api.service';
import { AuthService } from '../services/Auth/auth.service';
import { Country } from '../models/country.model';
import { Currency } from '../models/currency.model';
import { forkJoin } from 'rxjs';
import { SERVICES } from '../shared/constants/constants';

@Component({
  selector: 'app-banks-details',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  templateUrl: './banks-details.component.html',
  styleUrls: ['./banks-details.component.scss'],
})
export class BanksDetailsComponent implements OnInit {
  bank: BankReq | null = null;
  isLoading = true;
  errorMessage: string | null = null;
  
    // bring in the master list
  readonly allServices = SERVICES;
  // Add these properties
  countries: Country[] = [];
  currencies: Currency[] = [];
  currentCountry?: Country;
  currentCurrency?: Currency;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private bankApiService: BankApiService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    const codeBank = this.route.snapshot.paramMap.get('codeBank');

    if (!codeBank) {
      this.errorMessage = 'Bank code not provided';
      this.isLoading = false;
      return;
    }
  
    // Load all required data in parallel
    forkJoin([
      this.bankApiService.getBankByCode(codeBank),
      this.bankApiService.getAllCountries(),
      this.bankApiService.getAllCurrencies()
    ]).subscribe({
      next: ([bank, countries, currencies]) => {
        this.bank = bank;
        this.countries = countries;
        this.currencies = currencies;
        
        // Find matching country and currency
        this.currentCountry = this.countries.find(c => c.countryCode === bank.pCountryCode);
        this.currentCurrency = this.currencies.find(c => c.currencyCode === bank.pCurrencyCode);
        
        // Transform cardProducts into the expected format if necessary
        if (this.bank?.cardProducts && this.bank.cardProducts.length) {
          this.bank.cardProducts = (this.bank.cardProducts as any[]).map(cp => {
            // Create a new CardProduct object that nests the flat fields into an "info" property.
            return {
              info: {
                bankCode: cp.pBankCode || bank.pBankCode,  // fallback to bank's bankCode if needed
                description: cp.description,
                bin: cp.bin,
                plasticType: cp.plasticType,
                productType: cp.productType,
                productCode: cp.productCode,
                trancheMin: cp.trancheMin,
                trancheMax: cp.trancheMax,
                indexPvk: cp.indexPvk,
                serviceCode: cp.serviceCode,
                network: cp.network,
                expiration: cp.expiration,
                renew: cp.renew,
                priorExp: cp.priorExp,
              },
              fees: cp.fees,  // already nested correctly
              // If services is null or undefined, initialize as an empty object
              services: cp.services || {},
              // If limits is null or undefined, initialize as an empty array
              limits: cp.limits || []
            } as CardProduct;
          });
        }
        
        this.isLoading = false;
        console.log('Bank Details : ',bank);
        console.log('Bank Ressources : ',bank.ressources);
      },
      error: (err) => {
        this.handleError(err);
      }
    });
  }
  

  private handleError(err: any): void {
    console.error('Error loading data:', err);
    this.errorMessage = 'Failed to load bank details.';
    this.isLoading = false;
    
    if (err.status === 401) {
      this.authService.logout();
      this.router.navigate(['/login']);
    }
  }

 /**
   * Method to navigate back to the /banks page.
   */
  goBack(): void {
    this.router.navigate(['/banks']);
  }

  /**
   * Returns the icon class for a given service key.
   */
  getIcon(serviceKey: string): string {
    const service = this.allServices.find(s => s.name === serviceKey);
    return service?.icon || 'bi-question-circle';
  }

  /**
   * Returns an array of enabled service keys for a card product.
   */
  getEnabledServices(cardProduct: CardProduct): string[] {
    return this.allServices
      .filter(service => cardProduct.services[service.name])
      .map(service => service.name);
  }
  
}