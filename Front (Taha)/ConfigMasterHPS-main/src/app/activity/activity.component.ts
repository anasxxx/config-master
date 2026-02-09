import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { AuthService } from '../services/Auth/auth.service';


@Component({
  selector: 'app-activity',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, TranslateModule],
  templateUrl: './activity.component.html',
  styleUrls: ['./activity.component.scss'],
})
export class ActivityComponent implements OnInit {
  // Sidebar related properties
  sidebarExpanded = false;
  activityExpanded = false;
  isMobile = false;
  username = 'John Doe';



  // Modal related properties
  showProgressModal = false;
  progressStatus = '';
  overallProgress = 0;
  currentStepIndex = 0;
  testCompleted = false;

  constructor(private router: Router,
     private translate: TranslateService,
    private authService : AuthService) {}

  ngOnInit(): void {
    if (typeof window !== 'undefined') {
      this.checkScreenSize();
      window.addEventListener('resize', () => this.checkScreenSize());
    }
  }

  toggleActivity() {
    this.activityExpanded = !this.activityExpanded;
  }

  checkScreenSize(): void {
    if (typeof window !== 'undefined') {
      this.isMobile = window.innerWidth < 768;
    }
  }

  // Sidebar related methods
  toggleSidebar(): void {
    this.sidebarExpanded = !this.sidebarExpanded;

    // Add/remove overlay on mobile when sidebar is toggled
    if (this.isMobile) {
      if (this.sidebarExpanded) {
        this.addOverlay();
      } else {
        this.removeOverlay();
      }
    }
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
  }

  // Add overlay when sidebar is open on mobile
  addOverlay(): void {
    if (!document.querySelector('.sidebar-overlay')) {
      const overlay = document.createElement('div');
      overlay.className = 'sidebar-overlay active';
      overlay.addEventListener('click', () => this.toggleSidebar());
      document.body.appendChild(overlay);
    }
  }

  // Remove overlay when sidebar is closed
  removeOverlay(): void {
    const overlay = document.querySelector('.sidebar-overlay');
    if (overlay) {
      document.body.removeChild(overlay);
    }
  }

 

  

}
