// login.component.ts
import { Component, Inject, OnInit, PLATFORM_ID, HostListener } from '@angular/core';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { ContratistaApiService } from '../../services/contratista-api.service';
import { JwtService } from '../../services/jwt.service';
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
  pageLoaded: boolean = false;

  showPassword: boolean = false;
  capsLockActive: boolean = false;

  public showRutModal: boolean = false;
  public showEmailModal: boolean = false;
  public showCodeModal: boolean = false;
  public rutForRecovery: string = '';
  public emailForRecovery: string = '';
  public codeForRecovery: string = '';
  public rutErrorMessage: string = '';
  public emailErrorMessage: string = '';
  public codeErrorMessage: string = '';

  public rutLoginErrorMessage: string = '';
  
  public isCheckingRut: boolean = false;
  public isSendingCode: boolean = false;
  public isVerifyingCode: boolean = false;

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
      setTimeout(() => {
        this.pageLoaded = true;
      }, 500);
      
      this.cargarSociedadesGuardadas();
      
      if (this.jwtService.isAuthenticated()) {
        this.verifyAndNavigate();
      }
    }
  }

  @HostListener('document:keydown', ['$event'])
  @HostListener('document:keyup', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent): void {
    if (isPlatformBrowser(this.platformId)) {
      const activeElement = document.activeElement;
      if (activeElement && activeElement.id === 'password') {
        this.capsLockActive = event.getModifierState('CapsLock');
      }
    }
  }

  onPasswordBlur(): void {
    this.capsLockActive = false;
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  private validateRUT(rut: string): boolean {
    const cleanRut = rut.replace(/[^0-9kK]/g, '').toUpperCase();
    
    if (cleanRut.length < 2) return false;
    
    const body = cleanRut.slice(0, -1);
    const verifier = cleanRut.slice(-1);
    
    if (!/^\d+$/.test(body)) return false;
    
    let sum = 0;
    let multiplier = 2;
    
    for (let i = body.length - 1; i >= 0; i--) {
      sum += parseInt(body[i]) * multiplier;
      multiplier = multiplier === 7 ? 2 : multiplier + 1;
    }
    
    const expectedVerifier = 11 - (sum % 11);
    const calculatedVerifier = expectedVerifier === 11 ? '0' : 
                              expectedVerifier === 10 ? 'K' : 
                              expectedVerifier.toString();
    
    return verifier === calculatedVerifier;
  }

  verifyAndNavigate(): void {
    const token = this.jwtService.getToken();
    if (!token) {
      return;
    }

    this.contratistaApiService.verifyJWT(token).subscribe({
      next: (response: any) => {
        if (response.valid) {
          if (response.sociedades?.length > 0) {
            this.sociedades = response.sociedades;
            this.guardarSociedades();
          }

          const userInfo = response.user_info;
          
          if (userInfo.is_superuser) {
            this.router.navigate(['/super-admin']);
          } else {
            this.router.navigate(['/fs/home']);
          }
        } else {
          this.logout();
        }
      },
      error: () => {
        console.log('JWT inválido o expirado');
        this.logout();
      }
    });
  }

  login(): void {
    this.isLoading = true;
    this.isError = false;
    this.mensaje_login = 'Iniciando sesión...';

    if (!this.rut || !this.password) {
      this.showErrorMessage('Por favor complete todos los campos');
      return;
    }

    const cleanRut = this.rut.replace(/[^0-9kK]/g, '').toUpperCase();
    if (!this.validateRUT(cleanRut)) {
      this.showErrorMessage('RUT inválido');
      this.rutLoginErrorMessage = 'RUT inválido';
      return;
    }

    console.log('🚀 Iniciando login para RUT:', this.rut);

    this.contratistaApiService.login(this.rut, this.password, 'WEB')
      .subscribe({
        next: (data: any) => {
          console.log('✅ Login exitoso', data);
          
          if (data.autorizado) {
            this.jwtService.storeToken(data.jwt_token);
            if (data.refresh_token) {
              this.jwtService.storeRefreshToken(data.refresh_token);
            }

            if (data.sociedades?.length > 0) {
              console.log('🏢 Sociedades disponibles:', data.sociedades);
              this.sociedades = data.sociedades;
              this.guardarSociedades();
              
              if (data.sociedades.length === 1) {
                this.sociedadSeleccionada = data.sociedades[0];
                this.guardarSociedadSeleccionada();
                console.log('✅ Auto-seleccionada única sociedad:', data.sociedades[0]);
              }
            }

            this.clearLegacyTokens();

            this.isLoading = false;
            this.showMessage = false;

            if (data.redirect_to) {
              this.router.navigate([data.redirect_to]);
            } else {
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

  private guardarSociedades(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('sociedades', JSON.stringify(this.sociedades));
    }
  }

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

  private guardarSociedadSeleccionada(): void {
    if (isPlatformBrowser(this.platformId) && this.sociedadSeleccionada) {
      localStorage.setItem('sociedad_seleccionada', JSON.stringify(this.sociedadSeleccionada));
    }
  }

  onForgotPassword() {
    this.showRutModal = true;
  }

  checkRut() {
    if (!this.rutForRecovery.trim()) {
      this.rutErrorMessage = 'Por favor ingrese un RUT';
      return;
    }

    const rutClean = this.rutForRecovery.replace(/[^0-9kK]/g, '').toUpperCase();
    
    if (rutClean.length < 8) {
      this.rutErrorMessage = 'RUT incompleto';
      return;
    }

    if (!this.validateRUT(rutClean)) {
      this.rutErrorMessage = 'RUT inválido';
      return;
    }

    this.isCheckingRut = true;
    this.rutErrorMessage = '';

    this.contratistaApiService.post('password-reset/', { 
      action: 'check_user',
      rut_user: rutClean
    }).subscribe({
      next: (response: any) => {
        this.isCheckingRut = false;
        
        if (response.valid && response.status === 'success') {
          this.showRutModal = false;
          this.showEmailModal = true;
          this.rutErrorMessage = '';
          this.toastr.success('RUT encontrado', 'Éxito');
        } else {
          this.rutErrorMessage = 'RUT no encontrado en el sistema';
        }
      },
      error: (error) => {
        this.isCheckingRut = false;
        this.rutErrorMessage = 'RUT no encontrado en el sistema';
      }
    });
  }

  onRutInputChange() {
    this.rutErrorMessage = '';
  }

  onEmailInputChange() {
    this.emailErrorMessage = '';
  }

  onCodeInputChange() {
    this.codeErrorMessage = '';
  }

  sendCode() {
    if (!this.emailForRecovery.trim()) {
      this.emailErrorMessage = 'Por favor ingrese un email';
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.emailForRecovery)) {
      this.emailErrorMessage = 'Formato de email inválido';
      return;
    }

    this.isSendingCode = true;
    this.emailErrorMessage = '';
    const rutWithoutFormat = this.rutForRecovery.replace(/\D/g, '');

    this.contratistaApiService.post('password-reset/', { 
      action: 'generate_code',
      email: this.emailForRecovery, 
      rut: rutWithoutFormat 
    }).subscribe({
      next: (response: any) => {
        this.isSendingCode = false;
        
        if (response.status === 'success') {
          this.showEmailModal = false;
          this.showCodeModal = true;
          this.emailErrorMessage = '';
          this.toastr.success('Código enviado exitosamente', 'Éxito');
        } else {
          this.emailErrorMessage = response.message || 'Correo no encontrado o no coincide con el RUT';
        }
      },
      error: (error) => {
        this.isSendingCode = false;
        this.emailErrorMessage = error.error?.message || 'Correo no encontrado o no coincide con el RUT';
      }
    });
  }

  verifyCode() {
    if (!this.codeForRecovery.trim()) {
      this.codeErrorMessage = 'Por favor ingrese el código';
      return;
    }

    if (this.codeForRecovery.length !== 6) {
      this.codeErrorMessage = 'El código debe tener 6 dígitos';
      return;
    }

    this.isVerifyingCode = true;
    this.codeErrorMessage = '';
    const rutWithoutFormat = this.rutForRecovery.replace(/\D/g, '');

    this.contratistaApiService.post('password-reset/', { 
      action: 'verify_code',
      rut: rutWithoutFormat, 
      codigo: this.codeForRecovery 
    }).subscribe({
      next: (response: any) => {
        this.isVerifyingCode = false;
        
        if (response.status === 'success') {
          this.codeErrorMessage = '';
          this.toastr.success('Código verificado exitosamente', 'Éxito');
          this.router.navigate(['/change-password'], { 
            queryParams: { 
              rut: rutWithoutFormat, 
              code: this.codeForRecovery 
            }
          });
        } else {
          this.codeErrorMessage = response.message || 'Código inválido o expirado';
        }
      },
      error: (error) => {
        this.isVerifyingCode = false;
        this.codeErrorMessage = error.error?.message || 'Código inválido o expirado';
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
    this.rutErrorMessage = '';
    this.emailErrorMessage = '';
    this.codeErrorMessage = '';
  }

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

  logout(): void {
    console.log('🚪 Logout...');
    this.jwtService.clearTokens();
    
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
      this.rutLoginErrorMessage = '';
      return;
    }
    
    const verifier = rut.slice(-1);
    let body = rut.slice(0, -1);
    
    if (body.length === 0) {
      target.value = verifier;
      this.rutLoginErrorMessage = '';
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
    
    if (rut.length >= 8) {
      if (!this.validateRUT(rut)) {
        this.rutLoginErrorMessage = 'RUT inválido';
      } else {
        this.rutLoginErrorMessage = '';
      }
    } else {
      this.rutLoginErrorMessage = '';
    }
    
    const lengthDiff = formatted.length - rut.length;
    target.setSelectionRange(
      cursorPosition + lengthDiff, 
      cursorPosition + lengthDiff
    );
  }
}