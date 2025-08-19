// Archivo: services/smart-preload.component.ts
import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { Router } from '@angular/router';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { JwtService } from './jwt.service';

@Component({
  selector: 'app-smart-preload',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="smart-preload-container" [ngClass]="backgroundClass">
      <div class="loading-spinner" *ngIf="isLoading">
        <div class="spinner"></div>
        <p>Cargando...</p>
      </div>
    </div>
  `,
  styles: [`
    .smart-preload-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      width: 100vw;
      transition: background 0.3s ease;
    }
    
    .neutral-background {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .app-background {
      background: #f5f5f5; /* Fondo similar a tu aplicación */
    }
    
    .loading-spinner {
      text-align: center;
      color: white;
    }
    
    .spinner {
      border: 4px solid #f3f3f3;
      border-top: 4px solid #3498db;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
      margin: 0 auto 20px;
    }
    
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `]
})
export class SmartPreloadComponent implements OnInit {
  isLoading = true;
  backgroundClass = 'neutral-background';

  constructor(
    private router: Router,
    private jwtService: JwtService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.checkAuthenticationAndNavigate();
    }
  }

  private checkAuthenticationAndNavigate(): void {
    // Verificar inmediatamente si está autenticado
    if (this.jwtService.isAuthenticated() && !this.jwtService.isTokenExpired()) {
      // Usuario autenticado - usar fondo de app y navegar rápido
      this.backgroundClass = 'app-background';
      
      const payload = this.jwtService.decodeToken();
      if (payload?.is_superuser) {
        this.router.navigate(['/super-admin']);
      } else {
        this.router.navigate(['/fs/home']);
      }
    } else {
      // No autenticado - navegar a login
      this.router.navigate(['/login']);
    }
  }
}