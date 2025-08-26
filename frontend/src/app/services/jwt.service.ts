// src/app/services/jwt.service.ts - VERSIÓN ACTUALIZADA CON PERMISOS REALES
import { Injectable } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Inject, PLATFORM_ID } from '@angular/core';

// Probar diferentes formas de importar CryptoJS
let CryptoJS: any;

try {
  CryptoJS = require('crypto-js');
} catch (error) {
  try {
    import('crypto-js').then(crypto => {
      CryptoJS = crypto;
    });
  } catch (error2) {
  }
}

interface JWTPayload {
  user_id: number;
  user_type: 'SUPERADMIN' | 'ADMIN_HOLDING' | 'USER_NORMAL';
  holding_id: number | null;
  is_superuser: boolean;
  is_admin: boolean;
  perfil?: {
    id: number;
    nombre: string;
    tipo: 'WEB' | 'MOVIL' | 'AMBOS';
    estado: boolean;
  };
  permissions: {
    web?: { [modulo: string]: string[] };
    movil?: { [modulo: string]: string[] };
    superadmin_access?: boolean;
  };
  allowed_routes: string[];
  nombre_completo: string;
  rut: string;
  exp: number;
}

@Injectable({
  providedIn: 'root'
})
export class JwtService {
  private readonly JWT_TOKEN_KEY = 'jwt_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private readonly SALT = 'CONTRATISTA_2024';
  
  // Cache para SSR y browser
  private tokenCache: string | null = null;
  private refreshTokenCache: string | null = null;

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {
    this.initializeCryptoJS();
    this.initializeTokens();
  }

  /**
   * ✅ COMPATIBILIDAD SSR: Solo inicializar tokens si estamos en browser
   */
  private initializeTokens(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.preloadTokensFromStorage();
    } 
  }

  /**
   * ✅ PRECARGAR: Solo si estamos en browser
   */
  private preloadTokensFromStorage(): void {
    if (!this.isStorageAvailable()) {
      return;
    }

    try {
      this.tokenCache = localStorage.getItem(this.JWT_TOKEN_KEY);
      this.refreshTokenCache = localStorage.getItem(this.REFRESH_TOKEN_KEY);
      
      
    } catch (error) {
      this.tokenCache = null;
      this.refreshTokenCache = null;
    }
  }

  /**
   * ✅ VERFICACIÓN ROBUSTA: Compatible con SSR
   */
  private isStorageAvailable(): boolean {
    return isPlatformBrowser(this.platformId) && 
           typeof window !== 'undefined' && 
           typeof localStorage !== 'undefined';
  }

  /**
   * ✅ GET TOKEN: Compatible con SSR
   */
  getToken(): string | null {

    
    // En servidor, el token siempre será null
    if (!isPlatformBrowser(this.platformId)) {
      return null;
    }

    // Primero verificar el cache
    if (this.tokenCache) {
      return this.tokenCache;
    }

    // Si no hay cache, intentar localStorage
    if (this.isStorageAvailable()) {
      try {
        const token = localStorage.getItem(this.JWT_TOKEN_KEY);
        if (token) {
          this.tokenCache = token; // Actualizar cache
          return token;
        }
      } catch (error) {
      }
    }

    return null;
  }

  /**
   * ✅ GET REFRESH TOKEN: Compatible con SSR
   */
  getRefreshToken(): string | null {
    if (!isPlatformBrowser(this.platformId)) {
      return null;
    }

    // Primero verificar el cache
    if (this.refreshTokenCache) {
      return this.refreshTokenCache;
    }

    // Si no hay cache, intentar localStorage
    if (this.isStorageAvailable()) {
      try {
        const refreshToken = localStorage.getItem(this.REFRESH_TOKEN_KEY);
        if (refreshToken) {
          this.refreshTokenCache = refreshToken; // Actualizar cache
          return refreshToken;
        }
      } catch (error) {
        console.error('❌ Error accediendo localStorage para refresh token:', error);
      }
    }

    return null;
  }

  /**
   * ✅ STORE TOKEN: Solo en browser
   */
  storeToken(token: string): void {
    
    // Actualizar cache inmediatamente (disponible en SSR y browser)
    this.tokenCache = token;
    
    // Solo almacenar en localStorage si estamos en browser
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    // Almacenar en localStorage si está disponible
    if (this.isStorageAvailable()) {
      try {
        localStorage.setItem(this.JWT_TOKEN_KEY, token);
      } catch (error) {
        console.error('❌ Error almacenando token en localStorage:', error);
      }
    } else {
    }
  }

  /**
   * ✅ STORE REFRESH TOKEN: Solo en browser
   */
  storeRefreshToken(refreshToken: string): void {
    // Actualizar cache inmediatamente
    this.refreshTokenCache = refreshToken;
    
    // Solo almacenar en localStorage si estamos en browser
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    // Almacenar en localStorage si está disponible
    if (this.isStorageAvailable()) {
      try {
        localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
      } catch (error) {
        console.error('❌ Error almacenando refresh token:', error);
      }
    }
  }

  /**
   * ✅ IS AUTHENTICATED: Compatible con SSR
   */
  isAuthenticated(): boolean {
    
    // En servidor, considerar como no autenticado (se verificará en browser)
    if (!isPlatformBrowser(this.platformId)) {
      return false;
    }
    
    const token = this.getToken();
    if (!token) {
      return false;
    }

    const isExpired = this.isTokenExpired(token);
    const result = !isExpired;
    
   

    return result;
  }

  /**
   * ✅ CLEAR TOKENS: Compatible con SSR
   */
  clearTokens(): void {
    
    // Limpiar cache inmediatamente (disponible en SSR y browser)
    this.tokenCache = null;
    this.refreshTokenCache = null;
    
    // Solo limpiar localStorage si estamos en browser
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    // Limpiar localStorage si está disponible
    if (this.isStorageAvailable()) {
      try {
        localStorage.removeItem(this.JWT_TOKEN_KEY);
        localStorage.removeItem(this.REFRESH_TOKEN_KEY);
        
        // Limpiar también tokens legacy
        const legacyKeys = [
          'token', 'usuario_id', 'holding_id', 'is_admin', 
          'is_superuser', 'token_expiration', 'nombre_user', 
          'nombre_holding', 'submodulos_web', 'sociedad_actual', 
          'campo_actual'
        ];
        
        legacyKeys.forEach(key => {
          localStorage.removeItem(key);
        });
        
      } catch (error) {
        console.error('❌ Error limpiando localStorage:', error);
      }
    }
    

  }

  
  // ============================================
  // ✅ MÉTODOS DE PERMISOS ACTUALIZADOS
  // ============================================

  decodeToken(token?: string): JWTPayload | null {
    try {
      const jwtToken = token || this.getToken();
      if (!jwtToken) return null;

      const parts = jwtToken.split('.');
      if (parts.length !== 3) return null;

      const payload = parts[1];
      const paddedPayload = payload + '==='.slice(0, (4 - payload.length % 4) % 4);
      const decodedPayload = atob(paddedPayload.replace(/-/g, '+').replace(/_/g, '/'));
      
      return JSON.parse(decodedPayload) as JWTPayload;
    } catch (error) {
      console.error('Error decodificando JWT:', error);
      return null;
    }
  }

  isTokenExpired(token?: string): boolean {
    const payload = this.decodeToken(token);
    if (!payload || !payload.exp) return true;

    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp < currentTime;
  }

  /**
   * ✅ ACTUALIZADO: Verifica si el usuario tiene acceso a una ruta específica
   */
  canAccessRoute(route: string): boolean {
    const payload = this.decodeToken();
    if (!payload) return false;

    // Los superadmins pueden acceder a /super-admin
    if (payload.is_superuser && route.startsWith('/super-admin')) {
      return true;
    }

    // Verificar rutas permitidas
    return payload.allowed_routes?.includes(route) || false;
  }

  /**
   * ✅ ACTUALIZADO: Verifica si el usuario tiene acceso a un módulo específico
   */
  canAccessModule(modulo: string, tipo: 'web' | 'movil' = 'web'): boolean {
    const payload = this.decodeToken();
    if (!payload) return false;

    // Superadmins tienen acceso total
    if (payload.is_superuser) return true;

    // Verificar en permisos del tipo especificado
    const modulePermissions = payload.permissions[tipo];
    return modulePermissions ? Object.keys(modulePermissions).includes(modulo) : false;
  }

  /**
   * ✅ ACTUALIZADO: Verifica si el usuario tiene acceso a un submódulo específico
   */
  canAccessSubmodule(modulo: string, submodulo: string, tipo: 'web' | 'movil' = 'web'): boolean {
    const payload = this.decodeToken();
    if (!payload) return false;

    // Superadmins tienen acceso total
    if (payload.is_superuser) return true;

    // Verificar en permisos específicos
    const modulePermissions = payload.permissions[tipo];
    const submodules = modulePermissions?.[modulo];
    
    return submodules?.includes(submodulo) || false;
  }

  /**
   * ✅ ACTUALIZADO: Obtiene todos los módulos disponibles para el usuario
   */
  getAvailableModules(tipo: 'web' | 'movil' = 'web'): string[] {
    const payload = this.decodeToken();
    if (!payload) return [];

    const modulePermissions = payload.permissions[tipo];
    return modulePermissions ? Object.keys(modulePermissions) : [];
  }

  /**
   * ✅ ACTUALIZADO: Obtiene información básica del usuario logueado
   */
  getUserInfo(): { 
    user_id: number; 
    nombre: string; 
    user_type: string; 
    holding_id: number | null;
    perfil?: any;
  } | null {
    const payload = this.decodeToken();
    if (!payload) return null;

    return {
      user_id: payload.user_id,
      nombre: payload.nombre_completo,
      user_type: payload.user_type,
      holding_id: payload.holding_id,
      perfil: payload.perfil
    };
  }

  /**
   * ✅ NUEVO: Obtiene los submódulos de un módulo específico
   */
  getSubmodulesForModule(moduleName: string, tipo: 'web' | 'movil' = 'web'): string[] {
    const payload = this.decodeToken();
    if (!payload) return [];

    const modulePermissions = payload.permissions[tipo];
    return modulePermissions?.[moduleName] || [];
  }

  /**
   * ✅ NUEVO: Verifica si el usuario puede crear/editar en un módulo
   */
  canModifyInModule(moduleName: string, tipo: 'web' | 'movil' = 'web'): boolean {
    // Por ahora, si puede acceder al módulo, puede modificar
    // En el futuro puedes agregar permisos más granulares
    return this.canAccessModule(moduleName, tipo);
  }

  /**
   * ✅ NUEVO: Obtiene el perfil completo del usuario
   */
  getUserProfile(): any {
    const payload = this.decodeToken();
    return payload?.perfil || null;
  }

  /**
   * ✅ ACTUALIZADO: Genera estructura de navegación basada en permisos reales
   */
  generateNavigationStructure(): any[] {
    const payload = this.decodeToken();
    if (!payload) return [];

    // Para superadmins, estructura simple
    if (payload.is_superuser) {
      return [
        {
          label: 'Administración de Sistema',
          route: '/super-admin',
          icon: 'admin_panel_settings'
        }
      ];
    }

    // Para usuarios normales, generar basado en permisos web
    const navigation: any[] = [];
    const webPermissions = payload.permissions.web || {};

    Object.keys(webPermissions).forEach(modulo => {
      const submodulos = webPermissions[modulo];
      
      navigation.push({
        label: modulo,
        icon: this.getModuleIcon(modulo),
        children: submodulos.map(submodulo => ({
          label: submodulo,
          route: this.getRouteForSubmodule(submodulo),
          icon: this.getSubmoduleIcon(submodulo)
        }))
      });
    });

    return navigation;
  }

  /**
   * ✅ ACTUALIZADO: Mapea submódulos a rutas del frontend
   */
  private getRouteForSubmodule(submodulo: string): string {
    // ✅ MAPEO ACTUALIZADO para coincidir exactamente con app.routes.ts
    const routeMap: { [key: string]: string } = {
      // ADMINISTRACION
      'PERSONAL': '/fs/personal-empresas',
      'PERFILES': '/fs/administrar-perfiles',
      'USUARIOS': '/fs/administrar-usuarios',
      'AREAS/CARGOS ADMINISTRACION': '/fs/areas-cargos-administracion',
      'PARAMETROS ADMINISTRACION': '/fs/admin-sociedad',
      
      // RECURSOS HUMANOS
      'CONTRATACION PERSONAL': '/fs/autoregistro-personal',
      'CREAR CONTRATO': '/fs/generar-contrato',
      'CONTRATOS FIRMADOS': '/fs/generar-contrato',
      'PRODUCCION TRABAJADOR': '/fs/produccion-trabajador',
      'PARAMETROS RECURSOS HUMANOS': '/fs/r-h-afp',
      
      // CLIENTES
      'ADMINISTRAR CLIENTES': '/fs/administrar-clientes',
      'AREA/CARGOS CLIENTES': '/fs/administrar-area-cargos-cliente',
      'CONTACTOS': '/fs/administrar-contactos-clientes',
      
      // COMERCIAL
      'ACUERDO COMERCIAL': '/fs/folio-comercial',
      'PARAMETROS COMERCIAL': '/fs/labores-comercial',
      
      // TRANSPORTE
      'TRANSPORTISTAS': '/fs/empresas-transporte',
      'VEHICULOS': '/fs/vehiculos-transporte',
      'CHOFERES': '/fs/choferes-transporte',
    };

    return routeMap[submodulo] || '/fs/home';
  }

  /**
   * ✅ ACTUALIZADO: Obtiene iconos para módulos
   */
  private getModuleIcon(modulo: string): string {
    const iconMap: { [key: string]: string } = {
      'ADMINISTRACION': 'settings',
      'RECURSOS HUMANOS': 'people',
      'CLIENTES': 'business',
      'COMERCIAL': 'store',
      'TRANSPORTE': 'local_shipping',
      'GESTION TRABAJADORES': 'group',
      'MANO DE OBRA': 'construction',
      'COSECHA': 'agriculture'
    };
    return iconMap[modulo] || 'folder';
  }

  /**
   * ✅ Obtiene iconos para submódulos
   */
  private getSubmoduleIcon(submodulo: string): string {
    return 'arrow_forward_ios';
  }

  // ============================================
  // ✅ MÉTODOS DE CRYPTO (SIN CAMBIOS SIGNIFICATIVOS)
  // ============================================

  private async initializeCryptoJS(): Promise<void> {
    if (isPlatformBrowser(this.platformId)) {
      try {
        if (!CryptoJS) {
          const cryptoModule = await import('crypto-js');
          CryptoJS = cryptoModule.default || cryptoModule;
        }
      } catch (error) {
        console.error('❌ Failed to load CryptoJS:', error);
      }
    }
  }

  isCryptoAvailable(): boolean {
    return typeof CryptoJS !== 'undefined' && CryptoJS !== null;
  }

  hashPasswordWithDynamicSalt(password: string, rut: string, dynamicSalt: string): string {
    if (!isPlatformBrowser(this.platformId)) {
      throw new Error('Hash de contraseña no disponible en servidor');
    }

    try {
      const combined = password + rut + dynamicSalt;
      const hash = CryptoJS.SHA256(combined).toString();
      return hash;
    } catch (error) {
      console.error('❌ Error hasheando password:', error);
      throw new Error('Error generando hash de contraseña');
    }
  }
}