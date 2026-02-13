import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import { map } from 'rxjs/operators';
import { isPlatformBrowser, NgClass, NgFor, NgIf } from '@angular/common';
import { AuthService } from '../services/Auth/auth.service';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { HttpResponse } from '@angular/common/http';
import { User, LoginRes, LoginReq } from '../models/user.model';

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
  imports: [
    NgIf,
    NgClass,
    ReactiveFormsModule,
    NgbModule,
    TranslateModule,
    NgFor,
  ],
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  isSubmitted = false;
  loginError = false;
  errorMessage = '';
  isLoading = false;
  user = new User();
  selectedAccountType: string | null = null;

  // Define email mappings
  private readonly EMAIL_MAPPINGS = {
    DEMO: 'demo@gmail.com',
    FULL: 'full@gmail.com'
  };

  constructor(
    private formBuilder: FormBuilder,
    private router: Router,
    private authService: AuthService,
    private translate: TranslateService,
    @Inject(PLATFORM_ID) private platformId: any
  ) {}

  ngOnInit(): void {
    this.loginForm = this.formBuilder.group({
      email: ['', [Validators.required]],
      password: ['', [Validators.required]],
      rememberMe: [false],
    });
  }

  get formControls() {
    return this.loginForm.controls;
  }

  /**
   * Sets the email field value based on the selected account type
   */
  selectAccountType(type: string): void {
    this.selectedAccountType = type;
    const email = this.EMAIL_MAPPINGS[type as keyof typeof this.EMAIL_MAPPINGS];
    this.loginForm.patchValue({ email });
  }

  togglePasswordVisibility(): void {
    const passwordInput = document.getElementById(
      'password'
    ) as HTMLInputElement;
    const eyeIcon = document.querySelector('.bi-eye, .bi-eye-slash');
    if (passwordInput.type === 'password') {
      passwordInput.type = 'text';
      eyeIcon?.classList.replace('bi-eye', 'bi-eye-slash');
    } else {
      passwordInput.type = 'password';
      eyeIcon?.classList.replace('bi-eye-slash', 'bi-eye');
    }
  }

  onSubmit(): void {
    this.isSubmitted = true;
    this.loginError = false;

    if (this.loginForm.invalid) return;

    this.isLoading = true;

    // Create LoginReq instance
    const loginPayload = new LoginReq(
      this.loginForm.value.email,
      this.loginForm.value.password
    );

    this.authService
      .login(loginPayload)
      .pipe(
        map((response: HttpResponse<LoginRes>) => {
          // Convert raw response to LoginRes instance
          if (!response.body) return null;
          return new LoginRes(response.body.email, response.body.token);
        })
      )
      .subscribe({
        next: (loginRes: LoginRes | null) => {
          if (loginRes?.token) {
            const rememberMe = this.loginForm.value.rememberMe;
            this.authService.saveToken(loginRes.token, rememberMe);
            this.router.navigate(['/home']);
          }
          this.isLoading = false;
        },
        error: (err) => {
          this.loginError = true;
          this.errorMessage =
            err.error?.message ||
            this.translate.instant('login.errors.invalid_credentials');
          this.isLoading = false;
        },
      });
  }
}