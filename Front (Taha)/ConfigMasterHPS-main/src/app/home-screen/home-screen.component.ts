import { Component, HostListener, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../services/Auth/auth.service';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { CommonModule } from '@angular/common';
import { BankService } from '../services/bank.service';


@Component({
  selector: 'app-home-screen',
  templateUrl: './home-screen.component.html',
  standalone: true,
  imports: [TranslateModule, RouterModule, CommonModule],
  styleUrls: ['./home-screen.component.scss'],
})
export class HomeScreenComponent implements OnInit {
  sidebarExpanded = false; // Default to collapsed for all screens
  isMobile = false;
  username = 'User';
  pageTitle = 'home.title';
  // New property for Activity toggle
  activityExpanded = false;

  constructor(
    private router: Router,
    private authService: AuthService,
    private translate: TranslateService,
    private bankService : BankService
  ) {}

  ngOnInit() {
    this.checkScreenSize();
    this.updateUsername();
    this.bankService.initializeBankRequest();
    console.log('isFullUser:', this.authService.isFullUser());
    console.log('isDemoUser:', this.authService.isDemoUser());
  }

  @HostListener('window:resize', ['$event'])
  onResize() {
    this.checkScreenSize();
  }

  checkScreenSize() {
    if (typeof window !== 'undefined') {
      this.isMobile = window.innerWidth < 768;
      if (this.isMobile) {
        this.sidebarExpanded = false;
      }
    }
  }

  toggleSidebar() {
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

  // Add overlay when sidebar is open on mobile
  addOverlay() {
    if (!document.querySelector('.sidebar-overlay')) {
      const overlay = document.createElement('div');
      overlay.className = 'sidebar-overlay active';
      overlay.addEventListener('click', () => this.toggleSidebar());
      document.body.appendChild(overlay);
    }
  }

  // Remove overlay when sidebar is closed
  removeOverlay() {
    const overlay = document.querySelector('.sidebar-overlay');
    if (overlay) {
      document.body.removeChild(overlay);
    }
  }

  updateUsername() {
    if (this.authService.isFullUser()) {
      this.username = 'Full Profile';
    } else if (this.authService.isDemoUser()) {
      this.username = 'Demo Profile';
    } else {
      this.username = 'User'; // Fallback
    }
  }
  

  getUserInitials(): string {
    return this.username.slice(0, 2).toUpperCase();
  }

  logout() {
    this.authService.logout();
  }

  // New method to toggle Activity sub-items
  toggleActivity() {
    this.activityExpanded = !this.activityExpanded;
  }
}
