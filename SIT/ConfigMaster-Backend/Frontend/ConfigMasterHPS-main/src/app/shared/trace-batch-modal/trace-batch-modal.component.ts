import { Component, Input, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { CommonModule } from '@angular/common';
import { TraceBatchModel } from '../../models/trace-batch.model';

@Component({
  selector: 'app-trace-batch-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './trace-batch-modal.component.html',
  styleUrls: ['./trace-batch-modal.component.scss']
})
export class TraceBatchModalComponent implements OnInit {
  /**
   * List of trace batch items to display in the modal
   */
  @Input() traceBatches: TraceBatchModel[] = [];

  constructor(public activeModal: NgbActiveModal) {}

  ngOnInit() {
    console.log('Modal TraceBatch list received:', this.traceBatches);
  }

  /**
   * Helpers to determine whether any batch in the list has this data
   */
  hasShellReturnCodes(): boolean {
    return this.traceBatches.some(batch => batch.shellReturnCodes?.length > 0);
  }

  hasPowerCardReturnCodes(): boolean {
    return this.traceBatches.some(batch => batch.powerCardReturnCodes?.length > 0);
  }

  hasCardholderProcessed(): boolean {
    return this.traceBatches.some(batch => batch.cardholder_Processed?.length > 0);
  }

  hasCardholderPassed(): boolean {
    return this.traceBatches.some(batch => batch.cardholder_Passed?.length > 0);
  }

  hasCardholderRejected(): boolean {
    return this.traceBatches.some(batch => batch.cardholder_Rejected?.length > 0);
  }
/**
 * Parse a ddMMyyyy string into a Date at local midnight.
 */
getDateFromDMY(dateStr: string): Date {
  const day   = parseInt(dateStr.slice(0, 2), 10);
  const month = parseInt(dateStr.slice(2, 4), 10) - 1; // zero-based
  const year  = parseInt(dateStr.slice(4, 8), 10);
  return new Date(year, month, day);
}

  
}
