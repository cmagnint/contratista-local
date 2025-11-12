// login.component.ts - VERSIÓN ACTUALIZADA CON API UNIFICADA
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

  // Estados para los modales de recuperación
  public showRutModal: boolean = false;
  public showEmailModal: boolean = false;
  public showCodeModal: boolean = false;
  public rutForRecovery: string = '';
  public emailForRecovery: string = '';
  public codeForRecovery: string = '';
  
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

  onForgotPassword() {
    this.showRutModal = true;
  }

  // ============================================
  // 🎯 MÉTODOS ACTUALIZADOS PARA API UNIFICADA
  // ============================================

  /**
   * ✅ ACTUALIZADO: Verifica si el RUT existe usando API unificada
   */
  checkRut() {
    console.log('🔍 Verificando RUT:', this.rutForRecovery);
    
    if (!this.rutForRecovery.trim()) {
      this.toastr.error('Por favor ingrese un RUT', 'Error');
      return;
    }

    // ✅ Limpiar y validar formato
    const rutClean = this.rutForRecovery.replace(/[^0-9kK]/g, '').toUpperCase();
    
    // Validar longitud mínima (ej: 7 dígitos + verificador)
    if (rutClean.length < 8) {
      this.toastr.error('RUT incompleto', 'Error');
      return;
    }

    console.log('📤 RUT limpio enviado:', rutClean);

    this.contratistaApiService.post('password-reset/', { 
      action: 'check_user',
      rut_user: rutClean  // Enviar sin puntos ni guión
    }).subscribe({
      next: (response: any) => {
        console.log('✅ Respuesta verificación RUT:', response);
        
        if (response.valid && response.status === 'success') {
          this.showRutModal = false;
          this.showEmailModal = true;
          this.toastr.success('RUT encontrado', 'Éxito');
          
        } else {
          console.log("RUt no encontrado")
          this.toastr.error('RUT no encontrado', 'Error');
        }
      },
      error: (error) => {
        console.error('❌ Error al verificar RUT:', error);
        this.toastr.error('Error al verificar RUT', 'Error');
      }
    });
  }

  /**
   * ✅ ACTUALIZADO: Envía código de verificación usando API unificada
   */
  sendCode() {
    console.log('📧 Enviando código para:', this.emailForRecovery);
    
    if (!this.emailForRecovery.trim()) {
      this.toastr.error('Por favor ingrese un email', 'Error');
      return;
    }

    const rutWithoutFormat = this.rutForRecovery.replace(/\D/g, '');

    // ✅ NUEVA API UNIFICADA con action
    this.contratistaApiService.post('password-reset/', { 
      action: 'generate_code',
      email: this.emailForRecovery, 
      rut: rutWithoutFormat 
    }).subscribe({
      next: (response: any) => {
        console.log('✅ Respuesta envío código:', response);
        
        if (response.status === 'success') {
          this.showEmailModal = false;
          this.showCodeModal = true;
          this.toastr.success('Código enviado exitosamente', 'Éxito');
        } else {
          this.toastr.error(response.message || 'Error al enviar código', 'Error');
        }
      },
      error: (error) => {
        console.error('❌ Error al enviar código:', error);
        const errorMsg = error.error?.message || 'Error al enviar código';
        this.toastr.error(errorMsg, 'Error');
      }
    });
  }

  /**
   * ✅ ACTUALIZADO: Verifica código usando API unificada
   */
  verifyCode() {
    console.log('🔐 Verificando código:', this.codeForRecovery);
    
    if (!this.codeForRecovery.trim()) {
      this.toastr.error('Por favor ingrese el código', 'Error');
      return;
    }

    const rutWithoutFormat = this.rutForRecovery.replace(/\D/g, '');

    // ✅ NUEVA API UNIFICADA con action
    this.contratistaApiService.post('password-reset/', { 
      action: 'verify_code',
      rut: rutWithoutFormat, 
      codigo: this.codeForRecovery 
    }).subscribe({
      next: (response: any) => {
        console.log('✅ Respuesta verificación código:', response);
        
        if (response.status === 'success') {
          this.toastr.success('Código verificado exitosamente', 'Éxito');
          // Redirigir al componente de cambio de contraseña
          this.router.navigate(['/change-password'], { 
            queryParams: { 
              rut: rutWithoutFormat, 
              code: this.codeForRecovery 
            }
          });
        } else {
          this.toastr.error(response.message || 'Código inválido', 'Error');
        }
      },
      error: (error) => {
        console.error('❌ Error al verificar código:', error);
        const errorMsg = error.error?.message || 'Error al verificar código';
        this.toastr.error(errorMsg, 'Error');
      }
    });
  }

  /**
   * ✅ CERRAR MODALES - Sin cambios
   */
  closeModal() {
    this.showRutModal = false;
    this.showEmailModal = false;
    this.showCodeModal = false;
    this.rutForRecovery = '';
    this.emailForRecovery = '';
    this.codeForRecovery = '';
  }

  // ============================================
  // 🎯 MÉTODOS AUXILIARES - Sin cambios
  // ============================================

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

    // Guardar posición del cursor
    const cursorPosition = target.selectionStart || 0;
    
    // Limpiar todo excepto números y K/k
    let rut = target.value.replace(/[^0-9kK]/g, '').toUpperCase();
    
    // Si está vacío, salir
    if (rut.length === 0) {
      target.value = '';
      return;
    }
    
    // Separar dígito verificador (último carácter)
    const verifier = rut.slice(-1);
    let body = rut.slice(0, -1);
    
    // Si solo hay un dígito, no formatear aún
    if (body.length === 0) {
      target.value = verifier;
      return;
    }
    
    // Formatear cuerpo con puntos
    const parts: string[] = [];
    while (body.length > 3) {
      parts.unshift(body.slice(-3));
      body = body.slice(0, -3);
    }
    if (body.length > 0) {
      parts.unshift(body);
    }
    
    // Construir RUT formateado
    const formatted = parts.join('.') + '-' + verifier;
    target.value = formatted;
    
    // Restaurar cursor (opcional, mejora UX)
    const lengthDiff = formatted.length - rut.length;
    target.setSelectionRange(
      cursorPosition + lengthDiff, 
      cursorPosition + lengthDiff
    );
  }
}