export interface Patch {
    idPatch: string;
    description: string;
    codeBancaire: string;
    proprietaire: string;
    dateCreate: string; // You might consider using 'Date' type and transforming it if needed
  }