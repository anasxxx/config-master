import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { catchError, Observable, throwError } from 'rxjs';
import { AuthService } from '../Auth/auth.service'; // Adjust the path if needed
import { Batch } from '../../models/batch.model';   // Import the model
import { Campagne } from '../../models/campagne.model';
import { TraceBatchModel } from '../../models/trace-batch.model';
import { SimulationResult } from '../../models/simulationResult.model';
import {environment} from '../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class CampagneTestService {
  private baseUrl = environment.apiUrl + '/simulation'; // Base URL for campagne test endpoints

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
    return new HttpHeaders();
  }

  /**
   * Get all batches for a given campagne from the backend.
   */
  getAllBatches(campagne: string): Observable<Batch[]> {
    const url = `${this.baseUrl}/batches/${campagne}`;
    return this.httpClient.get<Batch[]>(url, {
      headers: this.getHeaders(),
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Fetch list of Campagnes from backend.
   */
  getCampagne(profile: 'full' | 'demo'): Observable<Campagne[]> {
    const url = `${this.baseUrl}/campagneFull/${profile}`;
    return this.httpClient.get<Campagne[]>(url, {
      headers: this.getHeaders(),
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Trigger ITNRScript backOffice process.
   * Returns a confirmation message as a string.
   */
  triggerBackOfficeScript(campagne: string): Observable<string> {
    const url = `${this.baseUrl}/ITNRScript/backOffice/${campagne}`;
    return this.httpClient.get(url, {
      headers: this.getHeaders(),
      responseType: 'text',
    }).pipe(
      catchError(this.handleError)
    );
  }

  getSimulationResults(campagne: string): Observable<SimulationResult> {
    const url = `${this.baseUrl}/SimulationResult/${campagne}`;
    return this.httpClient.get<SimulationResult>(url, {
      headers: this.getHeaders(),
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
 * Download simulation results for a specific batch in a campagne.
 * Returns the response as a string.
 */
downloadSimulationResult(campagne: string, batchName: string): Observable<string> {
  const url = `${this.baseUrl}/download/${campagne}/${batchName}`;
  return this.httpClient.get(url, {
    headers: this.getHeaders(),
    responseType: 'text',
  }).pipe(
    catchError(this.handleError)
  );
}

/**
   * Get the trace batch details for a specific campagne and batch name.
   * @param campagne The campagne identifier.
   * @param batchName The name of the batch.
   * @returns An observable of TraceBatchModel.
   */
getTraceBatch(campagne: string, batchName: string): Observable<TraceBatchModel[]> {
  const url = `${this.baseUrl}/trace/${encodeURIComponent(campagne)}/${encodeURIComponent(batchName)}`;
  return this.httpClient
    .get<TraceBatchModel[]>(url, { headers: this.getHeaders() })
    .pipe(
      catchError(this.handleError)
    );
}

/**
 * Download golden copy zip file via POST, sending a plain‐text body.
 * Returns the response as a Blob for file download.
 */
downloadGoldenCopy(requestText: string): Observable<Blob> {
  const url = `${this.baseUrl}/golden-copy/download`;

  return this.httpClient
    .post(url, requestText, {
      headers: this.getHeaders(),     // your existing headers
      responseType: 'blob',           // tell HttpClient you want a Blob back
    })
    .pipe(
      catchError(this.handleError)    // preserve your error handling
    );
}


  /**
   * Error handler for HTTP requests.
   */
  private handleError(error: HttpErrorResponse): Observable<never> {
    console.error('An error occurred:', error);
    return throwError(() => error);
  }
}
