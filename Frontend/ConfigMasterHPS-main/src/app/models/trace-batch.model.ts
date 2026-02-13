// trace-batch.model.ts

export interface TraceBatchModel {
    batchName: string;
    batchStatus: string;
    batchProcessing: string;
    taskId: string;
    businessDate: string;
    systemDate: string;
    shellReturnCodes: string[];
    powerCardReturnCodes: string[];
    cardholder_Processed: string[];
    cardholder_Passed: string[];
    cardholder_Rejected: string[];
  }
  