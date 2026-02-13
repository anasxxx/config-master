// src/app/services/dashboard/dashboard.service.ts

import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { Transaction } from '../../models/transaction.model';
import { AuthService } from '../Auth/auth.service';
import {environment} from '../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class DashboardService {
  private apiRoot = environment.apiUrl;
  
  constructor(
    private http: HttpClient,
    private auth: AuthService
  ) {}

  private getHeaders(): HttpHeaders {
    const token = this.auth.getToken();
    return token
      ? new HttpHeaders({ Authorization: `Bearer ${token}` })
      : new HttpHeaders();
  }

  /**
   * Fetches transactions for a given bank code on a specific date.
   * @param codeBank  e.g. "HFCKEN"
   * @param date      in YYYY-MM-DD format, e.g. "2025-05-14"
   */
  getTransactions(codeBank: string, date: string): Observable<Transaction[]> {
    const url = `${this.apiRoot}/dashboard/transactions/${codeBank}/${date}`;
    return this.http
      .get<Transaction[]>(url, { headers: this.getHeaders() })
      .pipe(
        catchError((err: HttpErrorResponse) => {
          console.error('DashboardService.getTransactions error', err);
          return throwError(() => err);
        })
      );
  }
}
