export interface Transaction {
    transactionDate: string;           // e.g. "2025-05-02 00:00:00.0"
    issuingBank: string;              // e.g. "HFCKEN"
    totalTransaction: number;         // e.g. 1
    perApproved: string;              // e.g. "0.0%"
    perCancellationApproved: string;  // e.g. "0.0%"
    perCancellationRejected: string;  // e.g. "0.0%"
    perDeclinedFonc: string;          // e.g. "100.0%"
    perDeclinedTech: string;          // e.g. "0.0%"
  }
  