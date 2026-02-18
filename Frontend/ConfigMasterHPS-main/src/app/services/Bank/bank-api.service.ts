import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { BankReq } from '../../models/bank-req.model'; // Update path accordingly
import { AuthService } from '../Auth/auth.service'; // Update path accordingly
import { Country } from '../../models/country.model';
import { Currency } from '../../models/currency.model';
import { Resource } from '../../models/resource.models';
import {environment}from '../../../environments/environment';
@Injectable({
  providedIn: 'root',
})
export class BankApiService {
  private baseUrl = environment.apiUrl + '/banks'; // Base URL for bank-related endpoints
  private banksParamBaseUrl =environment.apiUrl + '/banksParam'; // New base URL for parameter endpoints

  constructor(
    private httpClient: HttpClient,
    private authService: AuthService
  ) {}

  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      Authorization: 'Bearer ' + this.authService.getToken(),
    });
  }

  // Add a new bank
  addBank(bank: BankReq): Observable<any> {
    return this.httpClient.post(`${this.baseUrl}/add`, bank, {
      headers: this.getHeaders(),
    });
  }

  // Edit an existing bank
  editBank(bank: BankReq): Observable<any> {
    return this.httpClient.post(`${this.baseUrl}/edit`, bank, {
      headers: this.getHeaders(),
    });
  }

  // Get all banks
  getAllBanks(): Observable<BankReq[]> {
    return this.httpClient.get<BankReq[]>(`${this.baseUrl}/getAll`, {
      headers: this.getHeaders(),
    });
  }

  // Delete a bank by code
  deleteBank(code: string): Observable<string> {
    return this.httpClient.delete(
      `${this.baseUrl}/delete/${code}`,
      { responseType: 'text',
        headers : this.getHeaders()
       }
    );
  }

  // Get all currencies
  getAllCurrencies(): Observable<Currency[]> {
    // Replace 'any' with a proper model if available
    return this.httpClient.get<any[]>(`${this.banksParamBaseUrl}/currency`, {
      headers: this.getHeaders(),
    });
  }

  // Get all countries
  getAllCountries(): Observable<Country[]> {
    // Replace 'any' with a proper model if available
    return this.httpClient.get<any[]>(`${this.banksParamBaseUrl}/country`, {
      headers: this.getHeaders(),
    });
  }

  // Get all resources
  getAllResources(): Observable<Resource[]> {
    return this.httpClient.get<Resource[]>( // Specify the expected return type as an array of Resource
      `${this.banksParamBaseUrl}/Resources`, // Append '/Resources' to the parameter base URL
      { headers: this.getHeaders() } // Include the authorization headers
    );
  }

  // Get a bank by its code
  getBankByCode(codeBank: string): Observable<BankReq> {
    return this.httpClient.get<BankReq>(
      `${this.baseUrl}/getBank/${codeBank}`,
      { headers: this.getHeaders() }
    );
  }
}
