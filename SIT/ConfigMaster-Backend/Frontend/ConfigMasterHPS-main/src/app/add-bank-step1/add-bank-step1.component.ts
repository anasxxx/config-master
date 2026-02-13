import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { FormsModule } from '@angular/forms';
import { CommonModule, DatePipe } from '@angular/common';
import { NgbTooltip } from '@ng-bootstrap/ng-bootstrap';

import { NewBranchModule } from '../models/new-branch-module.model';
import { BankReq } from '../models/bank-req.model';
import { Country } from '../models/country.model';
import { Currency } from '../models/currency.model';
// This is the model for displaying available resource options
import { Resource } from '../models/resource.models';
// This is the model for the resources array in BankReq (the target structure)
import { MigResourcesModule } from '../models/mig-resources-module.model';
import {HARDCODED_RESOURCE_WORDINGS} from '../shared/constants/constants'
import { BankService } from '../services/bank.service';
import { BankApiService } from '../services/Bank/bank-api.service';
import { SideBarTestComponent } from '../side-bar-test/side-bar-test.component';
import { AuthService } from '../services/Auth/auth.service';


@Component({
  selector: 'app-add-bank-step1',
  standalone: true,
  imports: [TranslateModule, FormsModule, CommonModule, SideBarTestComponent, NgbTooltip],
  templateUrl: './add-bank-step1.component.html',
  styleUrls: ['./add-bank-step1.component.scss'],
  providers: [DatePipe],
})
export class AddBankStep1Component implements OnInit {
  countries: Country[] = [];
  currencies: Currency[] = [];
  // availableResources will be populated with Resource objects
  availableResources: Resource[] = [];
  isLoadingCountries = true;
  isLoadingCurrencies = true;
  isLoadingResources = false; // Will be false after synchronous setup
  loadError: string | null = null;

  currentStep = 1;
  showModal = false;
  isEditing = false;
  currentAgency: NewBranchModule = {
    bankCode: '',
    branchCode: '',
    branchWording: '',
    regionCode: '',
    regionWording: '',
    cityCode: '',
    cityWording: '',
  };
  selectedIndex = -1;
  agencies: NewBranchModule[] = [];

  bankData = {
    pBankWording: '',
    pCountryCode: '',
    pCurrencyCode: '',
    pBankCode: '',
  };

  // Keys are resource.resource_id, values are boolean (selected or not)
  selectedResources: { [resourceId: string]: boolean } = {};
  resourceSelectionInvalid = false;

  constructor(
    private router: Router,
    private bankService: BankService,
    private datePipe: DatePipe,
    private BankApiService: BankApiService,
    private AuthService : AuthService
  ) {}

  ngOnInit(): void {
    this.loadInitialData();
    this.loadSavedData();
    this.AuthService.loadToken();
  }

    // expose the check to the template
    public get isDemo(): boolean {
      return this.AuthService.isDemoUser();
    }

  private loadInitialData(): void {
    this.isLoadingCountries = true;
    this.isLoadingCurrencies = true;
    this.isLoadingResources = true; // Set true briefly
    this.loadError = null;

    this.BankApiService.getAllCountries().subscribe({
      next: (countries) => {
        this.countries = countries;
        this.isLoadingCountries = false;
      },
      error: (err) => {
        console.error('Error loading countries:', err);
        this.loadError = 'Failed to load countries. ';
        this.isLoadingCountries = false;
      },
    });

    this.BankApiService.getAllCurrencies().subscribe({
      next: (currencies) => {
        this.currencies = currencies;
        this.isLoadingCurrencies = false;
      },
      error: (err) => {
        console.error('Error loading currencies:', err);
        this.loadError = (this.loadError || '') + 'Failed to load currencies. ';
        this.isLoadingCurrencies = false;
      },
    });

    // Populate availableResources from the hardcoded list
    // Assuming Resource model has 'resource_id' and 'abrv_wording'
    // If your Resource model (resource.models.ts) is different, adjust the mapping.
    // For example, if Resource is { id: string, name: string }, map accordingly.
    this.availableResources = HARDCODED_RESOURCE_WORDINGS.map(wording => ({
      resource_id: wording, // Use wording as ID for simplicity
      abrv_wording: wording,
    })) as Resource[]; 

    this.isLoadingResources = false;

    // Initialize selections after availableResources is populated
    this.initializeResourceSelectionFromSavedData();
  }

  private loadSavedData(): void {
    const savedData = this.bankService.getBankRequest();
    if (savedData) {
      this.bankData = {
        pBankWording: savedData.pBankWording || '',
        pCountryCode: savedData.pCountryCode || '',
        pCurrencyCode: savedData.pCurrencyCode || '',
        pBankCode: savedData.pBankCode || '',
      };
      this.agencies = savedData.branches || [];

      // Ensure resources are available before trying to initialize selections
      if (this.availableResources.length > 0) {
        this.initializeResourceSelectionFromSavedData();
      }
    }
  }

  private initializeResourceSelectionFromSavedData(): void {
    const savedData = this.bankService.getBankRequest();
    this.selectedResources = {}; // Reset

    // savedData.ressources is an array of MigResourcesModule
    if (savedData?.ressources && this.availableResources.length > 0) {
      savedData.ressources.forEach(savedResource => { // savedResource is MigResourcesModule
        // We match based on the wording.
        const matchingAvailableResource = this.availableResources.find(
          // Ensure availableRes has abrv_wording or the correct property name
          availableRes => availableRes.abrv_wording === savedResource.resourceWording
        );
        if (matchingAvailableResource && matchingAvailableResource.resource_id) {
          this.selectedResources[matchingAvailableResource.resource_id] = true;
        }
      });
    }
  }

  openAddModal() {
    this.isEditing = false;
    this.currentAgency = {
      bankCode: this.bankData.pBankCode,
      branchCode: '',
      branchWording: '',
      regionCode: '',
      regionWording: '',
      cityCode: '',
      cityWording: '',
    };
    this.showModal = true;
  }

  openEditModal(agency: NewBranchModule, index: number) {
    this.isEditing = true;
    this.currentAgency = { ...agency };
    this.selectedIndex = index;
    this.showModal = true;
  }

  closeModal() {
    this.showModal = false;
    this.selectedIndex = -1;
  }

  handleAgencySubmit() {
    this.currentAgency.bankCode = this.bankData.pBankCode;
    if (this.isEditing) {
      this.agencies[this.selectedIndex] = { ...this.currentAgency };
    } else {
      this.agencies.push({ ...this.currentAgency });
    }
    this.closeModal();
  }

  deleteAgency(index: number) {
    this.agencies.splice(index, 1);
  }

  get isFormValid(): boolean {
    // const atLeastOneResourceSelected = Object.values(this.selectedResources).some(isSelected => isSelected);
    // this.resourceSelectionInvalid = !atLeastOneResourceSelected; // Update flag if needed

    return (
      this.bankData.pBankWording.trim() !== '' &&
      this.bankData.pCountryCode.trim() !== '' &&
      this.bankData.pCurrencyCode.trim() !== '' &&
      this.bankData.pBankCode.trim() !== '' 
      // && atLeastOneResourceSelected // Add if resource selection is mandatory
    );
  }

  onResourceSelectionChange(resourceId: string, isSelected: boolean): void {
    this.selectedResources[resourceId] = isSelected;
    // Potentially update validation state if needed
    // const atLeastOneResourceSelected = Object.values(this.selectedResources).some(val => val);
    // this.resourceSelectionInvalid = !atLeastOneResourceSelected;
  }

  handleNextStep() {
    const formIsValid = this.isFormValid;

    if (formIsValid) {
      const now = new Date();
      const formattedDate = this.datePipe.transform(now, 'yyyy-MM-dd HH:mm:ss', 'UTC');

      if (!formattedDate) {
        console.error('Date formatting failed!');
        return;
      }

      // Construct the 'ressources' array with MigResourcesModule objects
      const selectedMigResources: MigResourcesModule[] = this.availableResources
        .filter(resource => resource.resource_id && this.selectedResources[resource.resource_id])
        .map(resource => ({ // This object structure matches MigResourcesModule
          bankCode: this.bankData.pBankCode,         // Dynamically from the form
          resourceWording: resource.abrv_wording,    // From the hardcoded list via Resource object
        }));

      const bankReq: BankReq = {
        pBusinessDate: formattedDate,
        pBankCode: this.bankData.pBankCode,
        pBankWording: this.bankData.pBankWording,
        pCountryCode: this.bankData.pCountryCode,
        pCurrencyCode: this.bankData.pCurrencyCode,
        p_action_flag: '1',
        cardProducts: [],
        branches: this.agencies,
        ressources: selectedMigResources, // Assign the correctly structured array
      };

      console.log('Bank Request (Sending to Service):', bankReq);
      this.bankService.setBankRequest(bankReq);
      this.router.navigate(['/addbank/step2']);
    } else {
      console.warn('Form is not valid.');
      // if (!Object.values(this.selectedResources).some(isSelected => isSelected)) {
      //   this.resourceSelectionInvalid = true; // Example: show error if no resource is selected
      // }
    }
  }

  getCountryName(code: string): string {
    const country = this.countries.find((c) => c.countryCode === code);
    return country ? country.wording : '';
  }

  getCurrencyName(code: string): string {
    const currency = this.currencies.find((c) => c.currencyCode === code);
    return currency ? currency.currencyName : '';
  }
}