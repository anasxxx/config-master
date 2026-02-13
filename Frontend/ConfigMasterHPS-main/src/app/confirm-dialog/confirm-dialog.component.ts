// confirm-dialog.component.ts
import { NgIf } from '@angular/common';
import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { Observable } from 'rxjs';

export interface ConfirmDialogData {
  title: string;
  message: string;
  confirmButtonText: string;
  cancelButtonText: string;
  confirmAction: () => Observable<any>; // Callback function that returns an Observable
}

@Component({
  selector: 'app-confirm-dialog',
  templateUrl: './confirm-dialog.component.html',
  imports: [NgIf],
  styleUrls: ['./confirm-dialog.component.scss']
})
export class ConfirmDialogComponent {
  processing = false;
  errorMessage: string | null = null;

  constructor(
    public dialogRef: MatDialogRef<ConfirmDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ConfirmDialogData
  ) {}

  onCancel(): void {
    this.dialogRef.close(false);
  }

  onConfirm(): void {
    this.processing = true;
    
    // Execute the provided callback function
    this.data.confirmAction().subscribe({
      next: (result) => {
        this.processing = false;
        this.dialogRef.close({ success: true, result }); // Return both success status and any result data
      },
      error: (err) => {
        this.processing = false;
        console.error('Error executing action:', err);
        this.errorMessage = 'Operation failed. Please try again.';
        
        setTimeout(() => {
          this.errorMessage = null;
        }, 5000);
      }
    });
  }
}