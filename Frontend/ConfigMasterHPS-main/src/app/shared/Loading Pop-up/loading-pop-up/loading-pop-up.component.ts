import { NgFor, NgIf } from '@angular/common';
import { Component, Inject, OnInit, OnDestroy } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

export interface LoadingDialogData {
  message?: string;
}

@Component({
  selector: 'app-loading-dialog',
  templateUrl: './loading-pop-up.component.html',
  imports: [NgFor, NgIf], // For standalone components
  styleUrls: ['./loading-pop-up.component.scss']
})
export class LoadingDialogComponent implements OnInit, OnDestroy {
  steps = [
    { title: 'Initialization', description: 'Preparing system configuration', duration: 6000 },
    { title: 'Data Validation', description: 'Verifying input parameters', duration: 12500 },
    { title: 'Processing', description: 'Executing operations', duration: 12000 },
    { title: 'Finalizing', description: 'Completing tasks', duration: 4500 }
  ];

  currentStepIndex = 0;
  overallProgress = 0;
  testCompleted = false;
  currentStepAnimatedProgress = 0;

  private progressIntervalId: any;
  
  // --- New properties for random pauses ---
  private isPaused = false; // Flag to indicate if the current step's progress is paused
  private pauseTimeoutId: any; // Stores the ID of the timeout used to resume from a pause

  // Configuration for pause behavior (tweak these values as needed)
  private readonly pauseProbability = 0.1; // 5% chance to pause per progress update tick
  private readonly minPauseDuration = 200;  // Minimum pause duration in milliseconds
  private readonly maxPauseDuration = 3000; // Maximum pause duration in milliseconds
  // --- End of new properties ---

  constructor(
    public dialogRef: MatDialogRef<LoadingDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: LoadingDialogData
  ) {}

  ngOnInit(): void {
    if (this.steps.length > 0) {
      this.startProcessingCurrentStep();
    } else {
      this.testCompleted = true;
      this.overallProgress = 100;
    }
  }

  private startProcessingCurrentStep(): void {
    // Reset pause state for the new step and clear any pending pause timeouts
    if (this.pauseTimeoutId) {
      clearTimeout(this.pauseTimeoutId);
      this.pauseTimeoutId = null;
    }
    this.isPaused = false;

    if (this.currentStepIndex >= this.steps.length) {
      this.testCompleted = true;
      this.overallProgress = 100;
      if (this.progressIntervalId) {
        clearInterval(this.progressIntervalId);
      }
      return;
    }

    const stepToProcess = this.steps[this.currentStepIndex];
    this.currentStepAnimatedProgress = 0;

    const updateFrequencyMilliseconds = 150; // How often progress attempts to update
    const totalUpdatesNeeded = Math.max(1, stepToProcess.duration / updateFrequencyMilliseconds);
    const progressIncrementPerUpdate = 100 / totalUpdatesNeeded;

    this.progressIntervalId = setInterval(() => {
      if (this.isPaused) {
        // If paused, do nothing in this tick. The setTimeout will unpause.
        return;
      }

      // --- Logic for random pause ---
      // Condition to check if a pause can occur (e.g., not when the step is almost complete)
      const canInitiatePause = this.currentStepAnimatedProgress < (100 - progressIncrementPerUpdate * 2);

      if (canInitiatePause && Math.random() < this.pauseProbability) {
        this.isPaused = true;
        const pauseDuration = Math.random() * (this.maxPauseDuration - this.minPauseDuration) + this.minPauseDuration;
        
        
        this.pauseTimeoutId = setTimeout(() => {
          this.isPaused = false;
          this.pauseTimeoutId = null;
          // Optional: Log when resuming for debugging
          // console.log(`Step ${this.currentStepIndex} ('${stepToProcess.title}'): Resuming progress.`);
        }, pauseDuration);
        
        return; // Exit this tick; progress will resume in a future tick after pause ends
      }
      // --- End of random pause logic ---

      this.currentStepAnimatedProgress += progressIncrementPerUpdate;
      this.updateOverallProgress();

      if (this.currentStepAnimatedProgress >= 100) {
        this.currentStepAnimatedProgress = 100;
        clearInterval(this.progressIntervalId);
        this.currentStepIndex++;
        this.startProcessingCurrentStep();
      }
    }, updateFrequencyMilliseconds);
  }

  private updateOverallProgress(): void {
    const numberOfSteps = this.steps.length;
    if (numberOfSteps === 0) {
      this.overallProgress = 100;
      return;
    }

    const completedStepsCount = this.currentStepIndex;
    let progressOfCurrentAnimatingStep = 0;
    if (!this.testCompleted && this.currentStepIndex < numberOfSteps) {
        progressOfCurrentAnimatingStep = this.currentStepAnimatedProgress;
    }

    this.overallProgress = ((completedStepsCount * 100) + progressOfCurrentAnimatingStep) / numberOfSteps;

    if (this.overallProgress > 100) {
      this.overallProgress = 100;
    }
    if (this.testCompleted) {
      this.overallProgress = 100;
    }
  }

  getStepStatus(index: number): string {
    if (this.testCompleted) return 'Completed';
    if (index < this.currentStepIndex) return 'Completed';
    if (index === this.currentStepIndex) {
        // Optionally, you could change status to 'Paused' if this.isPaused is true
        // and index === this.currentStepIndex, but the visual stop itself might be enough.
        return 'In Progress';
    }
    return 'Pending';
  }

  getStepProgress(index: number): number {
    if (this.testCompleted) return 100;
    if (index < this.currentStepIndex) return 100;
    if (index === this.currentStepIndex) {
      return this.currentStepAnimatedProgress;
    }
    return 0;
  }

  ngOnDestroy(): void {
    if (this.progressIntervalId) {
      clearInterval(this.progressIntervalId);
    }
    // Crucially, clear any pending pause timeout when the component is destroyed
    if (this.pauseTimeoutId) {
      clearTimeout(this.pauseTimeoutId);
    }
  }
}