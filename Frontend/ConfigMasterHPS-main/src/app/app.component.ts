// app.component.ts
import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { RouterModule } from '@angular/router';
import { NgbDropdownModule } from '@ng-bootstrap/ng-bootstrap';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { AuthService } from './services/Auth/auth.service';

interface LanguageOption {
  code: string;
  name: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterModule, NgbDropdownModule, TranslateModule, CommonModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
  currentLang = 'en';

  availableLanguages: LanguageOption[] = [
    { code: 'en', name: 'English' },
    { code: 'fr', name: 'Français' },
  ];

  constructor(
    private translateService: TranslateService,
    private authService: AuthService,
    @Inject(PLATFORM_ID) private platformId: any
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.currentLang = localStorage.getItem('preferredLanguage') || 'en';
      this.translateService.setDefaultLang('en');
      this.translateService.use(this.currentLang);
    }
    this.authService.loadToken();
  }

  switchLanguage(lang: string): void {
    if (isPlatformBrowser(this.platformId)) {
      this.currentLang = lang;
      this.translateService.use(lang);
      localStorage.setItem('preferredLanguage', lang);
    }
  }

  getCurrentLanguageName(): string {
    const language = this.availableLanguages.find(
      (lang) => lang.code === this.currentLang
    );
    return language ? language.name : 'English';
  }
}
