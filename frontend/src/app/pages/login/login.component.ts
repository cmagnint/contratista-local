// login.component.ts

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

  // Estados para los modales de recuperación
  public showRutModal: boolean = false;
  public showEmailModal: boolean = false;
  public showCodeModal: boolean = false;
  public rutForRecovery: string = '';
  public emailForRecovery: string = '';
  public codeForRecovery: string = '';

  // ✅ NUEVO: Variables para sociedades
  sociedades: Array<{ id: number; nombre: string; rol_sociedad: string }> = [];
  sociedadSeleccionada: { id: number; nombre: string; rol_sociedad: string } | null = null;

  constructor(
    private contratistaApiService: ContratistaApiService,
    private jwtService: JwtService,
    private router: Router,
    private toastr: ToastrService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      // ✅ NUEVO: Cargar sociedades guardadas
      this.cargarSociedadesGuardadas();
      
      // Verificar si ya hay un JWT token válido
      if (this.jwtService.isAuthenticated()) {
        this.verifyAndNavigate();
      }
    }
  }

  /**
   * Verifica el JWT token actual y navega si es válido
   * ✅ ACTUALIZADO: Ahora carga sociedades
   */
  verifyAndNavigate(): void {
    const token = this.jwtService.getToken();
    if (!token) {
      return;
    }

    this.contratistaApiService.verifyJWT(token).subscribe({
      next: (response: any) => {
        if (response.valid) {
          // ✅ NUEVO: Guardar sociedades si vienen en la respuesta
          if (response.sociedades?.length > 0) {
            this.sociedades = response.sociedades;
            this.guardarSociedades();
          }

          const userInfo = response.user_info;
          
          // Navegar según tipo de usuario
          if (userInfo.is_superuser) {
            this.router.navigate(['/super-admin']);
          } else {
            this.router.navigate(['/fs/home']);
          }
        } else {
          // Token inválido, limpiar
          this.logout();
        }
      },
      error: () => {
        console.log('JWT inválido o expirado');
        this.logout();
      }
    });
  }

  /**
   * 🎯 LOGIN PRINCIPAL
   * ✅ ACTUALIZADO: Ahora maneja sociedades
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

    console.log('🚀 Iniciando login para RUT:', this.rut);

    this.contratistaApiService.login(this.rut, this.password, 'WEB')
      .subscribe({
        next: (data: any) => {
          console.log('✅ Login exitoso', data);
          
          if (data.autorizado) {
            // Almacenar tokens JWT
            this.jwtService.storeToken(data.jwt_token);
            if (data.refresh_token) {
              this.jwtService.storeRefreshToken(data.refresh_token);
            }

            // ✅ NUEVO: Guardar sociedades
            if (data.sociedades?.length > 0) {
              console.log('🏢 Sociedades disponibles:', data.sociedades);
              this.sociedades = data.sociedades;
              this.guardarSociedades();
              
              // Auto-seleccionar si solo hay una sociedad
              if (data.sociedades.length === 1) {
                this.sociedadSeleccionada = data.sociedades[0];
                this.guardarSociedadSeleccionada();
                console.log('✅ Auto-seleccionada única sociedad:', data.sociedades[0]);
              }
            }

            // Limpiar tokens OAuth2 legacy
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
          console.error('❌ Error en login:', error);
          
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

  // ===============================================================
  // ✅ NUEVOS MÉTODOS PARA GESTIÓN DE SOCIEDADES
  // ===============================================================

  /**
   * ✅ NUEVO: Guardar sociedades en localStorage
   */
  private guardarSociedades(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('sociedades', JSON.stringify(this.sociedades));
    }
  }

  /**
   * ✅ NUEVO: Cargar sociedades guardadas desde localStorage
   */
  private cargarSociedadesGuardadas(): void {
    if (isPlatformBrowser(this.platformId)) {
      const sociedadesStr = localStorage.getItem('sociedades');
      const sociedadStr = localStorage.getItem('sociedad_seleccionada');
      
      if (sociedadesStr) {
        this.sociedades = JSON.parse(sociedadesStr);
      }
      if (sociedadStr) {
        this.sociedadSeleccionada = JSON.parse(sociedadStr);
      }
    }
  }

  /**
   * ✅ NUEVO: Guardar sociedad seleccionada en localStorage
   */
  private guardarSociedadSeleccionada(): void {
    if (isPlatformBrowser(this.platformId) && this.sociedadSeleccionada) {
      localStorage.setItem('sociedad_seleccionada', JSON.stringify(this.sociedadSeleccionada));
    }
  }

  // ===============================================================
  // MÉTODOS DE RECUPERACIÓN DE CONTRASEÑA (SIN CAMBIOS)
  // ===============================================================

  onForgotPassword() {
    this.showRutModal = true;
  }

  checkRut() {
    console.log('🔍 Verificando RUT:', this.rutForRecovery);
    
    if (!this.rutForRecovery.trim()) {
      this.toastr.error('Por favor ingrese un RUT', 'Error');
      return;
    }

    const rutClean = this.rutForRecovery.replace(/[^0-9kK]/g, '').toUpperCase();
    
    if (rutClean.length < 8) {
      this.toastr.error('RUT incompleto', 'Error');
      return;
    }

    console.log('📤 RUT limpio enviado:', rutClean);

    this.contratistaApiService.post('password-reset/', { 
      action: 'check_user',
      rut_user: rutClean
    }).subscribe({
      next: (response: any) => {
        console.log('✅ Respuesta verificación RUT:', response);
        
        if (response.valid && response.status === 'success') {
          this.showRutModal = false;
          this.showEmailModal = true;
          this.toastr.success('RUT encontrado', 'Éxito');
        } else {
          console.log("RUT no encontrado")
          this.toastr.error('RUT no encontrado', 'Error');
        }
      },
      error: (error) => {
        console.error('❌ Error al verificar RUT:', error);
        this.toastr.error('Error al verificar RUT', 'Error');
      }
    });
  }

  sendCode() {
    console.log('📧 Enviando código para:', this.emailForRecovery);
    
    if (!this.emailForRecovery.trim()) {
      this.toastr.error('Por favor ingrese un email', 'Error');
      return;
    }

    const rutWithoutFormat = this.rutForRecovery.replace(/\D/g, '');

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

  verifyCode() {
    console.log('🔐 Verificando código:', this.codeForRecovery);
    
    if (!this.codeForRecovery.trim()) {
      this.toastr.error('Por favor ingrese el código', 'Error');
      return;
    }

    const rutWithoutFormat = this.rutForRecovery.replace(/\D/g, '');

    this.contratistaApiService.post('password-reset/', { 
      action: 'verify_code',
      rut: rutWithoutFormat, 
      codigo: this.codeForRecovery 
    }).subscribe({
      next: (response: any) => {
        console.log('✅ Respuesta verificación código:', response);
        
        if (response.status === 'success') {
          this.toastr.success('Código verificado exitosamente', 'Éxito');
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

  closeModal() {
    this.showRutModal = false;
    this.showEmailModal = false;
    this.showCodeModal = false;
    this.rutForRecovery = '';
    this.emailForRecovery = '';
    this.codeForRecovery = '';
  }

  // ===============================================================
  // MÉTODOS AUXILIARES (SIN CAMBIOS)
  // ===============================================================

  private showErrorMessage(message: string): void {
    this.mensaje_login = message;
    this.showMessage = true;
    this.isLoading = false;
    this.isError = true;
    this.toastr.error(message, 'Error');
  }

  private clearLegacyTokens(): void {
    if (isPlatformBrowser(this.platformId)) {
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
   * ✅ ACTUALIZADO: Logout completo - limpia tokens Y sociedades
   */
  logout(): void {
    console.log('🚪 Logout...');
    this.jwtService.clearTokens();
    
    // ✅ NUEVO: Limpiar sociedades
    this.sociedades = [];
    this.sociedadSeleccionada = null;
    
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('sociedades');
      localStorage.removeItem('sociedad_seleccionada');
    }
    
    this.router.navigate(['/login']);
    console.log('✅ Logout completado');
  }

  onSubmit(): void {
    this.showMessage = true;
    this.isLoading = true;
    this.mensaje_login = 'Iniciando sesión...';
    this.login();
  }
  
  formatRUT(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (!target) return;

    const cursorPosition = target.selectionStart || 0;
    let rut = target.value.replace(/[^0-9kK]/g, '').toUpperCase();
    
    if (rut.length === 0) {
      target.value = '';
      return;
    }
    
    const verifier = rut.slice(-1);
    let body = rut.slice(0, -1);
    
    if (body.length === 0) {
      target.value = verifier;
      return;
    }
    
    const parts: string[] = [];
    while (body.length > 3) {
      parts.unshift(body.slice(-3));
      body = body.slice(0, -3);
    }
    if (body.length > 0) {
      parts.unshift(body);
    }
    
    const formatted = parts.join('.') + '-' + verifier;
    target.value = formatted;
    
    const lengthDiff = formatted.length - rut.length;
    target.setSelectionRange(
      cursorPosition + lengthDiff, 
      cursorPosition + lengthDiff
    );
  }
}