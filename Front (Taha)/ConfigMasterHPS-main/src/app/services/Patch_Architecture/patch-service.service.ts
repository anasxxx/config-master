import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { catchError, Observable, of, throwError } from 'rxjs';
import { Architecte } from '../../models/architecte.model'; 
import { Patch } from '../../models/patch.model';           
import { AuthService } from '../Auth/auth.service';   
import { ContextBank } from '../../models/context-bank.model';  
import {environment} from '../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class PatchArchetService {
  private baseUrl = environment.apiUrl + '/PatchArchetContext'; // Base URL for patch architecture endpoints

  constructor(
    private httpClient: HttpClient,
    private authService: AuthService
  ) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    if (token) {
      return new HttpHeaders({
        Authorization: 'Bearer ' + token,
      });
    }
    return new HttpHeaders(); // Return empty headers if no token or auth not needed
  }

  

  // Get all Patches
  getAllPatches(): Observable<Patch[]> {
    return this.httpClient.get<Patch[]>(`${this.baseUrl}/patch`, {
      headers: this.getHeaders(),
    });
  }

  /**
   * Get the list of Architectes for Node 1 by codeBank.
   * If none are found (e.g. HTTP 404), returns the "Aucun..." message.
   */
  getArchitectureNode1(codeBank: string): Observable<Architecte[] | string> {
    const url = `${this.baseUrl}/ArchitectureNode1/${codeBank}`;
    return this.httpClient
      .get<Architecte[]>(url, { headers: this.getHeaders() })
      .pipe(
        catchError((err: HttpErrorResponse) => {
          if (err.status === 404) {
            // Not found → return your custom message
            return of('Aucune architecture trouvée pour le node 1.');
          }
          // propagate other errors
          return throwError(err);
        })
      );
  }

  /**
   * Get the list of Architectes for Node 2 by codeBank.
   * If none are found (e.g. HTTP 404), returns the "Aucun..." message.
   */
  getArchitectureNode2(codeBank: string): Observable<Architecte[] | string> {
    const url = `${this.baseUrl}/ArchitectureNode2/${codeBank}`;
    return this.httpClient
      .get<Architecte[]>(url, { headers: this.getHeaders() })
      .pipe(
        catchError((err: HttpErrorResponse) => {
          if (err.status === 404) {
            return of('Aucune architecture trouvée pour le node 2.');
          }
          return throwError(err);
        })
      );
  }

  /**
 * Get the context bank details by codeBank.
 * If none are found (e.g. HTTP 404), returns the "Aucun..." message.
 */
getContextBank(codeBank: string): Observable<ContextBank | string> {
  const url = `${this.baseUrl}/ContextBank/${codeBank}`;
  return this.httpClient
    .get<ContextBank>(url, { headers: this.getHeaders() })
    .pipe(
      catchError((err: HttpErrorResponse) => {
        if (err.status === 404) {
          return of('Aucun contexte trouvé pour cette banque.');
        }
        return throwError(() => err);
      })
    );
}

}