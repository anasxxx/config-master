import {
  Component,
  ElementRef,
  HostListener,
  OnInit,
  ViewChild
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-text-dialog',
  templateUrl: './text-dialog.component.html',
  imports: [FormsModule],
  styleUrls: ['./text-dialog.component.scss']
})
export class TextDialogComponent implements OnInit {
  /** Holds the user’s typed text */
  inputText: string = '';

  /** Reference to the backdrop element, to check click‐target */
  @ViewChild('backdrop', { static: true }) backdropRef!: ElementRef<HTMLDivElement>;

  constructor(private dialogRef: MatDialogRef<TextDialogComponent>) {}

  ngOnInit(): void {
    // Initially, OK button should be disabled (handled via [disabled] binding in template).
  }

  /** Called when the user types in the <input> */
  onInput(event: Event): void {
    // Since we use [(ngModel)], inputText is auto‐updated.
    // Method is here if you want additional logic in the future.
  }

  /** User clicked “Cancel” */
  handleCancel(): void {
    this.dialogRef.close(); 
  }

  /** User clicked “OK” */
  handleSubmit(): void {
    if (this.inputText.trim()) {
      this.dialogRef.close(this.inputText.trim());
    }
  }

  /** If user clicks on the backdrop (and not inside modal‐container), close */
  onBackdropClick(event: MouseEvent): void {
    // If click target is the backdrop itself, close; otherwise ignore.
    if (event.target === this.backdropRef.nativeElement) {
      this.handleCancel();
    }
  }

  /** Close on Escape key */
  @HostListener('document:keydown.escape', ['$event'])
  onEscape(event: KeyboardEvent) {
    this.handleCancel();
  }
}
