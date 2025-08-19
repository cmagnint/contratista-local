// login.component.ts - VERSIÓN SIMPLIFICADA ESTÁNDAR
import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { ContratistaApiService } from '../../services/contratista-api.service';
import { JwtService } from '../../services/jwt.service';
import { AnimationOptions } from 'ngx-lottie';
import { NewLinePipe } from '../../pipes/newline.pipe';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule, NewLinePipe],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent implements OnInit {
  rut: string = '';
  password: string = '';
  mensaje_login: string = '¡Bienvenido!\n\nPor favor ingrese su rut y su contraseña.';
  showMessage: boolean = true;
  isLoading: boolean = false;
  isError: boolean = false;
  lottieConfig: AnimationOptions = {
    path: 'assets/animations/loading.json',
    autoplay: true,
    loop: true
  };

  constructor(
    private contratistaApiService: ContratistaApiService,
    private jwtService: JwtService,
    private router: Router,
    private toastr: ToastrService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      // Verificar si ya hay un JWT token válido
      if (this.jwtService.isAuthenticated()) {
        this.verifyAndNavigate();
      }
    }
  }

  /**
   * Verifica el JWT token actual y navega si es válido
   */
  verifyAndNavigate(): void {
    const token = this.jwtService.getToken();
    if (!token) {
      return;
    }

    this.contratistaApiService.verifyJWT(token).subscribe({
      next: (response: any) => {
        if (response.valid) {
          const userInfo = response.user_info;
          
          // Navegar según tipo de usuario
          if (userInfo.is_superuser) {
            this.router.navigate(['/super-admin']);
          } else {
            this.router.navigate(['/fs/home']);
          }
        } else {
          // Token inválido, limpiar
          this.jwtService.clearTokens();
        }
      },
      error: () => {
        console.log('JWT inválido o expirado');
        this.jwtService.clearTokens();
      }
    });
  }

  /**
   * 🎯 LOGIN SIMPLE - ESTÁNDAR DE INDUSTRIA
   * Envía contraseña en texto plano sobre HTTPS
   */
  login(): void {
    this.isLoading = true;
    this.isError = false;
    this.mensaje_login = 'Iniciando sesión...';

    // Validar campos
    if (!this.rut || !this.password) {
      this.showErrorMessage('Por favor complete todos los campos');
      return;
    }

    console.log('🚀 Iniciando login estándar para RUT:', this.rut);

    // 🎯 USAR LOGIN SIMPLE - Tu LoginAPIView estándar
    this.contratistaApiService.login(this.rut, this.password, 'WEB')
      .subscribe({
        next: (data: any) => {
          console.log('✅ Login JWT estándar exitoso', data);
          
          if (data.autorizado) {
            // Almacenar tokens JWT
            this.jwtService.storeToken(data.jwt_token);
            if (data.refresh_token) {
              this.jwtService.storeRefreshToken(data.refresh_token);
            }

            // Limpiar tokens OAuth2 legacy si existen
            this.clearLegacyTokens();

            this.isLoading = false;
            this.showMessage = false;

            // Navegar según respuesta del backend
            if (data.redirect_to) {
              this.router.navigate([data.redirect_to]);
            } else {
              // Fallback basado en tipo de usuario
              if (data.user_type === 'SUPERADMIN') {
                this.router.navigate(['/super-admin']);
              } else {
                this.router.navigate(['/fs/home']);
              }
            }

            this.toastr.success('¡Bienvenido!', 'Login exitoso');
          } else {
            this.showErrorMessage(data.mensaje || 'Error de autenticación');
          }
        },
        error: (error) => {
          console.error('❌ Error en login estándar:', error);
          
          let errorMessage = 'Usuario o contraseña incorrectos';
          
          if (typeof error === 'string') {
            errorMessage = error;
          } else if (error.error?.mensaje) {
            errorMessage = error.error.mensaje;
          } else if (error.message) {
            errorMessage = error.message;
          }

          this.showErrorMessage(errorMessage);
        }
      });
  }

  /**
   * Muestra un mensaje de error y actualiza el estado
   */
  private showErrorMessage(message: string): void {
    this.mensaje_login = message;
    this.showMessage = true;
    this.isLoading = false;
    this.isError = true;
    this.toastr.error(message, 'Error');
  }

  /**
   * Limpia tokens OAuth2 legacy del localStorage
   * DEPRECATED: Solo para migración gradual
   */
  private clearLegacyTokens(): void {
    if (isPlatformBrowser(this.platformId)) {
      // Limpiar tokens y datos OAuth2 antiguos
      const legacyKeys = [
        'token', 'usuario_id', 'holding_id', 'is_admin', 
        'is_superuser', 'token_expiration', 'nombre_user', 
        'nombre_holding', 'submodulos_web', 'sociedad_actual', 
        'campo_actual'
      ];
      
      legacyKeys.forEach(key => {
        localStorage.removeItem(key);
      });
    }
  }

  /**
   * Logout completo - limpia todos los tokens JWT
   */
  logout(): void {
    console.log('🚪 Logout desde login component...');
    this.jwtService.clearTokens();
    this.router.navigate(['/login']);
    console.log('✅ Logout completado');
  }

  /**
   * Maneja el submit del formulario
   */
  onSubmit(): void {
    this.showMessage = true;
    this.isLoading = true;
    this.mensaje_login = 'Iniciando sesión...';
    this.login();
  }
  
  /**
   * Formatea el RUT mientras el usuario escribe
   */
  formatRUT(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (!target) return;

    let rut = target.value.replace(/\D/g, '');
    let parts = [];
    const verifier = rut.slice(-1);
    rut = rut.slice(0, -1);
    
    while (rut.length > 3) {
      parts.unshift(rut.slice(-3));
      rut = rut.slice(0, -3);
    }
    
    parts.unshift(rut);
    target.value = parts.join('.') + '-' + verifier;
    
    if (target.value === '-') {
      target.value = '';
    }
  }

  /**
   * DEBUG: Muestra información del JWT para desarrollo
   */
  debugJWT(): void {
    if (!isPlatformBrowser(this.platformId)) return;

    const debugInfo = this.contratistaApiService.getDebugInfo();
    console.log('=== DEBUG JWT INFO ===');
    console.log('Debug Info:', debugInfo);
    
    const payload = this.jwtService.decodeToken();
    console.log('JWT Payload:', payload);
    
    if (payload) {
      console.log('User Info:', this.jwtService.getUserInfo());
      console.log('Available Modules (web):', this.jwtService.getAvailableModules('web'));
      console.log('Can access /fs/perfiles:', this.jwtService.canAccessRoute('/fs/perfiles'));
      console.log('Can access ADMINISTRACION module:', this.jwtService.canAccessModule('ADMINISTRACION'));
      console.log('Navigation Structure:', this.jwtService.generateNavigationStructure());
    }
  }
}