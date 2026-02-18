import { Inject, Injectable, PLATFORM_ID } from '@angular/core';
import { LoginReq, LoginRes, User } from '../../models/user.model'; // Assuming User model has an email property if used by getUserInfo
import { Router } from '@angular/router';
import { JwtHelperService } from '@auth0/angular-jwt';
import { HttpClient, HttpResponse } from '@angular/common/http';
import { isPlatformBrowser } from '@angular/common';
import { Observable } from 'rxjs';
import {environment} from '../../../environments/environment'; // Adjusted import to use environment variables

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private helper = new JwtHelperService();
  token!: string;
  public loggedUser!: string; // Stores the username/email from JWT's 'sub' claim
  public isLoggedIn: boolean = false; // Changed Boolean to boolean for consistency
  private BackendURL = environment.apiUrl; // Variable d'environnement pour l'URL du backend 

  // --- Email constants for roles ---
  private readonly DEMO_USER_EMAIL = 'demo@gmail.com';
  private readonly FULL_USER_EMAIL = 'full@gmail.com';

  constructor(
    private router: Router,
    private httpClient: HttpClient,
    @Inject(PLATFORM_ID) private platformId: any
  ) {}

  login(loginReq: LoginReq): Observable<HttpResponse<LoginRes>> {
    return this.httpClient.post<LoginRes>(
      this.BackendURL + '/login',
      loginReq,
      { observe: 'response' }
    );
  }

  saveToken(jwt: string, rememberMe: boolean) {
    if (isPlatformBrowser(this.platformId)) {
      if (rememberMe) {
        localStorage.setItem('jwt', jwt);
        sessionStorage.removeItem('jwt');
      } else {
        sessionStorage.setItem('jwt', jwt);
        localStorage.removeItem('jwt');
      }
      this.token = jwt;
      this.isLoggedIn = true;
      this.decodedJWT(); // This will set this.loggedUser
    }
  }

  getToken(): string | undefined { // Adjusted return type for clarity
    return this.token;
  }

  decodedJWT() {
    if (this.token) { // Check if token is defined
      try {
        const decodedToken = this.helper.decodeToken(this.token);
        if (decodedToken && decodedToken.sub) {
          this.loggedUser = decodedToken.sub; // Assuming 'sub' claim is the email
        } else {
          console.error('JWT sub claim is missing or token is invalid after decoding.');
          this.clearAuthDataAndLogout(); // Or handle error appropriately
        }
      } catch (error) {
        console.error('Error decoding JWT:', error);
        this.clearAuthDataAndLogout(); // Or handle error appropriately
      }
    }
  }

  logout() {
    this.clearAuthDataAndLogout();
    this.router.navigate(['/login']);
  }

  // Helper method to centralize clearing of auth data
  private clearAuthDataAndLogout() {
    this.loggedUser = undefined!;
    this.isLoggedIn = false;
    this.token = undefined!;

    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('jwt');
      sessionStorage.removeItem('jwt');
      localStorage.removeItem('loggedUser'); // Legacy cleanup
      localStorage.removeItem('isLoggedIn'); // Legacy cleanup
    }
  }

  /**
   * @deprecated This method seems to have legacy logic. User info is primarily derived from JWT.
   */
  setLoggedUserLS(login: string) {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('loggedUser', login); // This might be for display purposes
      localStorage.setItem('isLoggedIn', 'true');
    }
    this.loggedUser = login; // Ensure this is the email if used for role checks
    this.isLoggedIn = true;
  }

  loadToken() {
    if (isPlatformBrowser(this.platformId)) {
      const localToken = localStorage.getItem('jwt');
      const sessionToken = sessionStorage.getItem('jwt');
      const tokenToVerify = localToken || sessionToken;

      if (tokenToVerify) {
        if (!this.helper.isTokenExpired(tokenToVerify)) {
          this.token = tokenToVerify;
          this.isLoggedIn = true;
          this.decodedJWT(); // This will set this.loggedUser
        } else {
          this.clearAuthDataAndLogout(); // Token expired, clear all auth data
          // Optionally, navigate to login or show a message
          // this.router.navigate(['/login']);
        }
      } else {
        // No token found, ensure state is clean
        this.isLoggedIn = false;
        this.loggedUser = undefined!;
        this.token = undefined!;
      }
    }
  }

  isTokenStillValid(): boolean { // Renamed for clarity, as isTokenExpired sounds negative
    if (!this.token) {
      return false;
    }
    return !this.helper.isTokenExpired(this.token);
  }

  /**
   * @deprecated Original isTokenExpired might be confusing if token is undefined. Use isTokenStillValid().
   */
  isTokenExpired(): boolean {
    // Returns true if the token is expired or if there is no token.
    // Consider using !this.isTokenStillValid() if you want to check if a user *should* be logged out.
    return !this.token || this.helper.isTokenExpired(this.token);
  }


  // --- New Role-Based Authorization Methods ---

  /**
   * Checks if the currently logged-in user is a "Demo" user.
   * Assumes `this.loggedUser` stores the email address from the JWT's 'sub' claim.
   * @returns {boolean} True if the logged-in user is a Demo user, false otherwise.
   */
  public isDemoUser(): boolean {
    if (this.isLoggedIn && this.loggedUser) {
      return this.loggedUser.toLowerCase() === this.DEMO_USER_EMAIL;
    }
    return false; // Not logged in or user identifier (email) is missing
  }

  /**
   * Checks if the currently logged-in user is a "Full" user.
   * Assumes `this.loggedUser` stores the email address from the JWT's 'sub' claim.
   * @returns {boolean} True if the logged-in user is a Full user, false otherwise.
   */
  public isFullUser(): boolean {
    if (this.isLoggedIn && this.loggedUser) {
      return this.loggedUser.toLowerCase() === this.FULL_USER_EMAIL;
    }
    return false; // Not logged in or user identifier (email) is missing
  }

  // --- End of New Role-Based Authorization Methods ---


  /**
   * Retrieves basic user information.
   * Note: The original implementation seemed to incorrectly use `this.loggedUser` as a key.
   * This revised version assumes `this.loggedUser` directly holds the email.
   * @returns {User | null} User object with email, or null if not logged in/no email.
   */
  getUserInfo(): User | null {
    if (this.isLoggedIn && this.loggedUser) {
      // Assuming this.loggedUser is the email.
      // The User model would need to be defined to match this structure, e.g., interface User { email: string; roles?: string[]; ... }
      return { email: this.loggedUser } as User; // Cast as User, ensure User model matches
    }
    return null;
  }
}