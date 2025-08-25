// change-password.component.ts
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { ContratistaApiService } from '../../services/contratista-api.service';

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.css']
})
export class ChangePasswordComponent implements OnInit {
  
  // Datos del formulario
  public nuevaContrasena: string = '';
  public confirmarContrasena: string = '';
  public isLoading: boolean = false;
  
  // Datos de verificación
  public rut: string = '';
  public codigo: string = '';
  
  // Estados del componente
  public showPassword: boolean = false;
  public showConfirmPassword: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private toastr: ToastrService,
    private contratistaApiService: ContratistaApiService
  ) {}

  ngOnInit(): void {
    // Obtener parámetros de la URL
    this.route.queryParams.subscribe(params => {
      this.rut = params['rut'] || '';
      this.codigo = params['code'] || '';
      
      console.log('📄 Parámetros recibidos:', { rut: this.rut, codigo: this.codigo });
      
      // Verificar que tengamos los parámetros necesarios
      if (!this.rut || !this.codigo) {
        this.toastr.error('Parámetros de verificación faltantes', 'Error');
        this.router.navigate(['/login']);
        return;
      }
    });
  }

  /**
   * ✅ Cambia la contraseña usando la API unificada
   */
  changePassword(): void {
    // Validaciones básicas
    if (!this.validarFormulario()) {
      return;
    }

    this.isLoading = true;
    console.log('🔐 Cambiando contraseña para RUT:', this.rut);

    // ✅ NUEVA API UNIFICADA con action
    this.contratistaApiService.post('password-reset/', {
      action: 'change_password',
      rut: this.rut,
      nuevaContrasena: this.nuevaContrasena,
      codigo: this.codigo  // Verificación de seguridad adicional
    }).subscribe({
      next: (response: any) => {
        console.log('✅ Respuesta cambio contraseña:', response);
        
        if (response.status === 'success') {
          this.toastr.success('Contraseña cambiada exitosamente', 'Éxito');
          
          // Limpiar formulario
          this.nuevaContrasena = '';
          this.confirmarContrasena = '';
          
          // Redirigir al login después de 2 segundos
          setTimeout(() => {
            this.router.navigate(['/login']);
          }, 2000);
          
        } else {
          this.toastr.error(response.message || 'Error al cambiar contraseña', 'Error');
        }
      },
      error: (error) => {
        console.error('❌ Error al cambiar contraseña:', error);
        
        let errorMessage = 'Error al cambiar contraseña';
        if (error.error?.message) {
          errorMessage = error.error.message;
        } else if (typeof error.error === 'string') {
          errorMessage = error.error;
        }
        
        this.toastr.error(errorMessage, 'Error');
      },
      complete: () => {
        this.isLoading = false;
      }
    });
  }

  /**
   * ✅ Valida el formulario antes de enviar
   */
  private validarFormulario(): boolean {
    // Verificar campos vacíos
    if (!this.nuevaContrasena.trim()) {
      this.toastr.error('Por favor ingrese la nueva contraseña', 'Error');
      return false;
    }

    if (!this.confirmarContrasena.trim()) {
      this.toastr.error('Por favor confirme la nueva contraseña', 'Error');
      return false;
    }

    // Verificar que las contraseñas coincidan
    if (this.nuevaContrasena !== this.confirmarContrasena) {
      this.toastr.error('Las contraseñas no coinciden', 'Error');
      return false;
    }

    // Verificar longitud mínima
    if (this.nuevaContrasena.length < 6) {
      this.toastr.error('La contraseña debe tener al menos 6 caracteres', 'Error');
      return false;
    }

    // Verificar que no sean parámetros de verificación
    if (!this.rut || !this.codigo) {
      this.toastr.error('Sesión de verificación inválida', 'Error');
      this.router.navigate(['/login']);
      return false;
    }

    return true;
  }

  /**
   * ✅ Toggle para mostrar/ocultar contraseña
   */
  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  /**
   * ✅ Toggle para mostrar/ocultar confirmación de contraseña
   */
  toggleConfirmPasswordVisibility(): void {
    this.showConfirmPassword = !this.showConfirmPassword;
  }

  /**
   * ✅ Cancelar y volver al login
   */
  cancelar(): void {
    if (this.nuevaContrasena || this.confirmarContrasena) {
      if (confirm('¿Está seguro que desea cancelar? Se perderán los cambios.')) {
        this.router.navigate(['/login']);
      }
    } else {
      this.router.navigate(['/login']);
    }
  }

  /**
   * ✅ Validación en tiempo real de coincidencia de contraseñas
   */
  onConfirmPasswordChange(): void {
    if (this.confirmarContrasena && this.nuevaContrasena !== this.confirmarContrasena) {
      // Puedes añadir una clase CSS para mostrar error visualmente
    }
  }

  // ============================================
  // 🎯 MÉTODOS PARA VALIDACIÓN DE FORTALEZA
  // ============================================

  /**
   * ✅ Verifica si la contraseña es débil
   */
  isWeakPassword(): boolean {
    return this.nuevaContrasena.length < 6;
  }

  /**
   * ✅ Verifica si la contraseña es media
   */
  isMediumPassword(): boolean {
    return this.nuevaContrasena.length >= 6 && this.nuevaContrasena.length < 8;
  }

  /**
   * ✅ Verifica si la contraseña es fuerte
   */
  isStrongPassword(): boolean {
    return this.nuevaContrasena.length >= 8 && 
           /[A-Z]/.test(this.nuevaContrasena) && 
           /[0-9]/.test(this.nuevaContrasena);
  }

  /**
   * ✅ Obtiene el texto de fortaleza de la contraseña
   */
  getPasswordStrengthText(): string {
    if (this.isStrongPassword()) return 'Fuerte';
    if (this.isMediumPassword()) return 'Media';
    if (this.isWeakPassword()) return 'Débil';
    return '';
  }

  /**
   * ✅ Obtiene la clase CSS para el indicador de fortaleza
   */
  getPasswordStrengthClass(): string {
    if (this.isStrongPassword()) return 'strong';
    if (this.isMediumPassword()) return 'medium';
    if (this.isWeakPassword()) return 'weak';
    return '';
  }
}