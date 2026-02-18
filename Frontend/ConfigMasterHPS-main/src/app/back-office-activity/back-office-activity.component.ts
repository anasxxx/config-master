import { NgClass, NgIf } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CampagneTestService } from '../services/SSH_CampaignTest/campagne-test.service';
import { Batch } from '../models/batch.model';
import { BatchResult } from '../models/batchResult.model';
import { AuthService } from '../services/Auth/auth.service';
import { HttpErrorResponse } from '@angular/common/http';
import { Campagne } from '../models/campagne.model';
import { TraceBatchModel } from '../models/trace-batch.model';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { TraceBatchModalComponent } from '../shared/trace-batch-modal/trace-batch-modal.component';
import { RapportResult } from '../models/RapportResult.model';
import { SimulationResult } from '../models/simulationResult.model';
import { TextDialogComponent } from '../text-dialog/text-dialog.component';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';

export interface Campaign {
  campagneName: string;
  campaignBatches?: Batch[];
  showBatchDetails?: boolean;
  isLaunching?: boolean;
  isLoadingBatches?: boolean;
  launchMessage?: string | null;
  simulationResultss?: SimulationResult[];
  showSimulationResults?: boolean;
  isLoadingResults?: boolean;
  // New properties for timer
  startTime?: number | null;
  elapsedTime?: string | null;
  timerInterval?: any;
}

@Component({
  selector: 'app-back-office-activity',
  standalone: true,
  imports: [NgClass, NgIf, TranslateModule, RouterModule, CommonModule],
  templateUrl: './back-office-activity.component.html',
  styleUrls: ['./back-office-activity.component.scss']
})
export class BackOfficeActivityComponent implements OnInit {
  campagnes: Campaign[] = [];
  sidebarExpanded = false;
  activityExpanded = false;
  isMobile = false;
  username = 'John Doe';
  isTraceLoading: boolean = false;
  isDownloadingGoldenPatch = false;

  constructor(
    private router: Router,
    private campagneTestService: CampagneTestService,
    private authService: AuthService,
    private modalService: NgbModal,
    private dialog: MatDialog 
  ) {}

  ngOnInit(): void {
    this.getUserInfo();
    this.fetchCampagnes();
  }

  fetchCampagnes(): void {
    let profile: 'full' | 'demo';
    if (this.authService.isFullUser()) {
      profile = 'full';
    } else if (this.authService.isDemoUser()) {
      profile = 'demo';
    } else {
      console.error('Unknown user profile');
      return;
    }
    this.campagneTestService.getCampagne(profile).subscribe({
      next: (data: Campagne[]) => {
        this.campagnes = data.map(campagne => ({
          campagneName: campagne.campagneName,
          campaignBatches: [],
          showBatchDetails: false,
          isLaunching: false,
          isLoadingBatches: false,
          launchMessage: null,
          simulationResultss: [],
          showSimulationResults: false,
          isLoadingResults: false,
          // Initialize timer properties
          startTime: null,
          elapsedTime: null,
          timerInterval: null
        }));
      },
      error: (error: HttpErrorResponse) => {
        console.error('Error fetching campagnes:', error.message);
      }
    });
  }

  launchCampaign(campaign: Campaign): void {
    campaign.isLaunching = true;
    campaign.launchMessage = null;
    
    // Reset timer and start new timer
    this.resetCampaignTimer(campaign);
    campaign.startTime = Date.now();
    campaign.timerInterval = setInterval(() => {
      this.updateElapsedTime(campaign);
    }, 1000);

    this.campagneTestService.triggerBackOfficeScript(campaign.campagneName).subscribe({
      next: (response: string) => {
        console.log('Campaign launch initiated successfully:', response);
        campaign.isLaunching = false;
        this.stopCampaignTimer(campaign);
        campaign.launchMessage = `${response} (${campaign.elapsedTime})`;
      },
      error: (error: HttpErrorResponse) => {
        console.error('Error launching campaign:', error.message);
        campaign.isLaunching = false;
        this.stopCampaignTimer(campaign);
        campaign.launchMessage = `Failed to launch campaign: ${error.message} (${campaign.elapsedTime})`;
      }
    });
  }

  // Helper to update elapsed time
  private updateElapsedTime(campaign: Campaign): void {
    if (campaign.startTime) {
      const elapsedMs = Date.now() - campaign.startTime;
      const seconds = Math.floor(elapsedMs / 1000);
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      campaign.elapsedTime = `${minutes} min ${remainingSeconds} s`;
    }
  }

  // Helper to stop and clear timer
  private stopCampaignTimer(campaign: Campaign): void {
    if (campaign.timerInterval) {
      clearInterval(campaign.timerInterval);
      campaign.timerInterval = null;
    }
    this.updateElapsedTime(campaign); // Final update
  }

  // Helper to reset timer
  private resetCampaignTimer(campaign: Campaign): void {
    this.stopCampaignTimer(campaign);
    campaign.startTime = null;
    campaign.elapsedTime = null;
  }

  // Other methods remain unchanged...
  toggleBatchDetails(campaign: Campaign): void {
    campaign.showBatchDetails = !campaign.showBatchDetails;
    if (campaign.showBatchDetails && (!campaign.campaignBatches || campaign.campaignBatches.length === 0)) {
      campaign.isLoadingBatches = true;
      this.campagneTestService.getAllBatches(campaign.campagneName).subscribe({
        next: (batches: Batch[]) => {
          campaign.campaignBatches = batches;
          campaign.isLoadingBatches = false;
        },
        error: (error: HttpErrorResponse) => {
          console.error('Error fetching batches:', error.message);
          campaign.showBatchDetails = false;
          campaign.isLoadingBatches = false;
          alert(`Failed to fetch batches: ${error.message}`);
        }
      });
    } else if (!campaign.showBatchDetails) {
      campaign.isLoadingBatches = false;
    }
  }

  toggleSimulationResults(campaign: Campaign): void {
    campaign.showSimulationResults = !campaign.showSimulationResults;
  
    if (campaign.showSimulationResults && (!campaign.simulationResultss || campaign.simulationResultss.length === 0)) {
      campaign.isLoadingResults = true;
  
      this.campagneTestService.getSimulationResults(campaign.campagneName).subscribe({
        next: (result: SimulationResult) => {
          // Put the entire SimulationResult object into the array
          campaign.simulationResultss = [ result ];
  
          campaign.isLoadingResults = false;
        },
        error: (error: HttpErrorResponse) => {
          console.error('Error fetching simulation results:', error.message);
          campaign.showSimulationResults = false;
          campaign.isLoadingResults = false;
          alert(`Failed to fetch simulation results: ${error.message}`);
        }
      });
  
    } else if (!campaign.showSimulationResults) {
      campaign.isLoadingResults = false;
    }
  }
  
  

  getStatusClass(status: string): string {
    if (!status) return 'status-not-ok';
    
    const statusUpper = status.toUpperCase().trim();
    
    return statusUpper === 'OK' ? 'status-ok' : 'status-not-ok';
  }

  downloadResult(campagneName: string, batchName: string): void {
    this.campagneTestService.downloadSimulationResult(campagneName, batchName).subscribe({
      next: (content: string) => {
        const blob = new Blob([content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${batchName}_results.txt`;
        a.click();
        window.URL.revokeObjectURL(url);
      },
      error: (error: HttpErrorResponse) => {
        console.error('Error downloading result:', error.message);
        alert(`Failed to download result: ${error.message}`);
      }
    });
  }

   // (1) Add this helper method:
   canDownload(batchName: string): boolean {
    return batchName === 'card_production' || batchName === 'pin_mailer_generation';
  }

  viewTraceBatch(campagneName: string, batchName: string): void {
    this.isTraceLoading = true;
    this.campagneTestService.getTraceBatch(campagneName, batchName).subscribe({
      next: (traceBatches: TraceBatchModel[]) => {
        const modalRef = this.modalService.open(TraceBatchModalComponent, {
          size: 'xl',
          centered: true,
          backdrop: 'static',
          keyboard: true
        });

        modalRef.componentInstance.traceBatches = traceBatches;

        setTimeout(() => {
          modalRef.componentInstance.traceBatches = traceBatches;
        }, 0);

        modalRef.result.then(
          result => console.log('Modal closed with result:', result),
          dismissed => console.log('Modal dismissed:', dismissed)
        );
        this.isTraceLoading = false;
      },
      error: (error: HttpErrorResponse) => {
        console.error('Error fetching trace batch list:', error.message);
        alert(`Failed to fetch trace batch details: ${error.message}`);
        this.isTraceLoading = false;
      }
    });
  }

  getStatusIcon(status: string): string {
    if (!status) return '❌';
    
    const statusUpper = status.toUpperCase().trim();
    
    return statusUpper === 'OK' ? '✅' : '❌';
  }

  getStatusColor(status: string): string {
    if (!status) return '#dc3545';
    
    const statusUpper = status.toUpperCase().trim();
    
    return statusUpper === 'OK' ? '#28a745' : '#dc3545';
  }

  getUserInitials(): string {
    return this.username
      .split(' ')
      .map((name) => name[0])
      .join('')
      .toUpperCase();
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  getUserInfo() {
    if (this.authService.isFullUser()) {
      this.username = 'Full Profile';
    } else if (this.authService.isDemoUser()) {
      this.username = 'Demo Profile';
    } else {
      this.username = 'User';
    }
  }

  toggleActivity() {
    this.activityExpanded = !this.activityExpanded;
  }

  addOverlay(): void {
    if (!document.querySelector('.sidebar-overlay')) {
      const overlay = document.createElement('div');
      overlay.className = 'sidebar-overlay active';
      overlay.addEventListener('click', () => this.toggleSidebar());
      document.body.appendChild(overlay);
    }
  }

  removeOverlay(): void {
    const overlay = document.querySelector('.sidebar-overlay');
    if (overlay) {
      document.body.removeChild(overlay);
    }
  }

  toggleSidebar(): void {
    this.sidebarExpanded = !this.sidebarExpanded;
    if (this.isMobile) {
      if (this.sidebarExpanded) {
        this.addOverlay();
      } else {
        this.removeOverlay();
      }
    }
  }

/** inside your component that has MatDialog injected… */
downloadGoldenPatch(): void {
  const dialogRef = this.dialog.open(TextDialogComponent, {
    width: '250px'  // you can adjust width/height as you like
  });

  dialogRef.afterClosed().subscribe((enteredText: string | undefined) => {
    if (!enteredText) {
      // user either clicked “Cancel” or didn’t type anything valid
      return;
    }

    this.isDownloadingGoldenPatch = true;
    this.campagneTestService
      .downloadGoldenCopy(enteredText)
      .subscribe({
        next: (blob: Blob) => {
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = 'golden-copy.zip';
          link.click();
          window.URL.revokeObjectURL(url);
          this.isDownloadingGoldenPatch = false;
        },
        error: (error: HttpErrorResponse) => {
          console.error('Error downloading golden copy:', error.message);
          alert(`Failed to download golden copy: ${error.message}`);
          this.isDownloadingGoldenPatch = false;
        }
      });
  });
}


  formatBatchName(name: string): string {
    if (!name) {
      return '';
    }
    return name.replace(/_/g, ' ').toUpperCase();
  }
}