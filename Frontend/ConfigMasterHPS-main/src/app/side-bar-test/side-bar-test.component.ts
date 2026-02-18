import { NgFor, NgIf } from '@angular/common';
import {
  Component,
  Input,
  Output,
  EventEmitter,
  ChangeDetectionStrategy,
  ElementRef,
  OnChanges,
  SimpleChanges,
} from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';

interface StepInfo {
  step: number;
  icon: string;
  titleKey: string;
}

@Component({
  selector: 'app-progress-steps-sidebar',
  standalone: true,
  imports: [NgFor, NgIf, TranslateModule],
  templateUrl: './side-bar-test.component.html',
  styleUrls: ['./side-bar-test.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SideBarTestComponent implements OnChanges {
  // Input to determine which step is currently active
  @Input() currentStep: number = 1;
  // Input to control sidebar visibility on mobile
  @Input() isSidebarVisible: boolean = true;
  @Input() nextDisabled: boolean = false;

  // Outputs to notify parent of navigation actions if needed
  @Output() nextStepClicked = new EventEmitter<void>();
  @Output() previousStepClicked = new EventEmitter<void>();
  @Output() submitClicked = new EventEmitter<void>();
  @Output() toggleSidebar = new EventEmitter<void>();

  // Define the steps data
  steps: StepInfo[] = [
    {
      step: 1,
      icon: 'bi-info-circle-fill',
      titleKey: 'banks.add.step1.title',
    },
    {
      step: 2,
      icon: 'bi-credit-card',
      titleKey: 'banks.add.step2.title',
    },
    {
      step: 3,
      icon: 'bi-journal-check',
      titleKey: 'banks.add.step3.title',
    },
  ];

  constructor(private el: ElementRef) {}

  ngOnChanges(changes: SimpleChanges) {
    if (changes['currentStep']) {
      // Update CSS variables to assist with any dynamic styling
      this.el.nativeElement.style.setProperty(
        '--current-step',
        this.currentStep
      );
      this.el.nativeElement.style.setProperty(
        '--total-steps',
        this.steps.length
      );
    }
  }

  // Advances to the next step with animation support via CSS
  onNextStep(): void {
    if (this.currentStep < this.steps.length) {
      this.currentStep++;
      this.nextStepClicked.emit();
    }
  }

  // Goes back to the previous step
  onPreviousStep(): void {
    if (this.currentStep > 1) {
      this.currentStep--;
      this.previousStepClicked.emit();
    }
  }

  // Called when the user finishes the process (last step)
  onSubmit(): void {
    this.submitClicked.emit();
  }

  // Helper function for template class binding
  isStepActive(stepNumber: number): boolean {
    return stepNumber === this.currentStep;
  }

  // Helper function to determine if a step is completed
  isStepCompleted(stepNumber: number): boolean {
    return stepNumber < this.currentStep;
  }

  // Method to toggle sidebar visibility on mobile
  onToggleSidebar(): void {
    this.toggleSidebar.emit();
  }
}
