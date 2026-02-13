import { Injectable } from '@angular/core';
import { BankReq } from '../models/bank-req.model';

@Injectable({
  providedIn: 'root',
})
export class BankService {
  private bankRequest!: BankReq;

  setBankRequest(request: BankReq): void {
    this.bankRequest = request;
  }

  getBankRequest(): BankReq {
    return this.bankRequest;
  }

  initializeBankRequest(): void {
    this.bankRequest = new BankReq();
  }
}
