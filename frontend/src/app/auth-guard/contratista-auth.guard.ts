// src/app/auth-guard/contratista-auth.guard.ts - VERSIÓN COMPATIBLE CON SSR
import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { PLATFORM_ID } from '@angular/core';
import { JwtService } from '../services/jwt.service';
import { ContratistaApiService } from '../services/contratista-api.service';
import { map, catchError, of } from 'rxjs';

/**
 * ✅ Auth Guard COMPATIBLE CON SSR
 * 
 * Estrategia:
 * 1. Si estamos en SERVER (SSR) → Permitir navegación y verificar en browser
 * 2. Si estamos en BROWSER → Verificar autenticación normal
 */
export const contratistaAuthGuard: CanActivateFn = (route, state) => {
  const jwtService = inject(JwtService);
  const apiService = inject(ContratistaApiService);
  const router = inject(Router);
  const platformId = inject(PLATFORM_ID);

  // ✅ DETECCIÓN SSR: Si estamos en servidor, permitir navegación
  if (!isPlatformBrowser(platformId)) {
    return true; // ← Permitir navegación, la verificación se hará en el browser
  }

  // ✅ VERIFICACIÓN NORMAL EN BROWSER (después de hidratación)
  return checkAuthenticationInBrowser(state.url, jwtService, apiService, router);
};

/**
 * ✅ Verificación de autenticación solo en browser
 */
function checkAuthenticationInBrowser(
  url: string, 
  jwtService: JwtService, 
  apiService: ContratistaApiService, 
  router: Router
): boolean | Promise<boolean> {
  

  // Verificar token
  const token = jwtService.getToken();
  
  if (!token) {
    router.navigate(['/login']);
    return false;
  }


  // Verificar si está expirado
  if (jwtService.isTokenExpired()) {
    
    // Aquí podrías implementar refresh logic si lo necesitas
    // Por ahora, limpiar y redirigir
    jwtService.clearTokens();
    router.navigate(['/login']);
    return false;
  }

  return checkRouteAccess(url, jwtService, router);
}

/**
 * ✅ Verificación de acceso a rutas
 */
function checkRouteAccess(url: string, jwtService: JwtService, router: Router): boolean {
  const payload = jwtService.decodeToken();
  
  if (!payload) {
    jwtService.clearTokens();
    router.navigate(['/login']);
    return false;
  }


  // SUPERADMIN: Verificación específica
  if (payload.is_superuser) {
    if (url.startsWith('/super-admin')) {
      return true;
    } else if (url.startsWith('/fs/')) {
      router.navigate(['/super-admin']);
      return false;
    }
    return true;
  }

  // USUARIOS NORMALES: No pueden acceder a /super-admin
  if (url.startsWith('/super-admin')) {
    router.navigate(['/fs/home']);
    return false;
  }

  // RUTAS /fs/: Verificar permisos básicos
  if (url.startsWith('/fs/')) {
    const hasWebModules = payload.permissions?.web && Object.keys(payload.permissions.web).length > 0;
    const hasMovilModules = payload.permissions?.movil && Object.keys(payload.permissions.movil).length > 0;
    
    if (hasWebModules || hasMovilModules) {
      return true;
    } else {
      router.navigate(['/fs/home']);
      return false;
    }
  }

  // RUTAS PÚBLICAS: Redirigir si ya está logueado
  if (url === '/login' || url === '/') {
    if (payload.is_superuser) {
      router.navigate(['/super-admin']);
    } else {
      router.navigate(['/fs/home']);
    }
    return false;
  }

  return true;
}

/**
 * ✅ GUARD SIMPLE COMPATIBLE CON SSR
 */
export const simpleAuthGuard: CanActivateFn = (route, state) => {
  const platformId = inject(PLATFORM_ID);
  
  // En servidor, permitir navegación
  if (!isPlatformBrowser(platformId)) {
    return true;
  }
  
  // En browser, verificar autenticación
  const jwtService = inject(JwtService);
  const router = inject(Router);


  if (!jwtService.isAuthenticated()) {
    router.navigate(['/login']);
    return false;
  }

  return true;
};

/**
 * ✅ GUARD PARA SOLO BROWSER (sin SSR)
 */
export const browserOnlyAuthGuard: CanActivateFn = (route, state) => {
  const platformId = inject(PLATFORM_ID);
  const jwtService = inject(JwtService);
  const router = inject(Router);


  // Bloquear completamente en servidor
  if (!isPlatformBrowser(platformId)) {
    return false;
  }

  // Verificación normal en browser
  if (!jwtService.isAuthenticated()) {
    router.navigate(['/login']);
    return false;
  }

  return checkRouteAccess(state.url, jwtService, router);
};

/**
 * ✅ GUARD CON VALIDACIÓN DIFERIDA
 * Permite la navegación pero valida después de la hidratación
 */
export const deferredAuthGuard: CanActivateFn = (route, state) => {
  const platformId = inject(PLATFORM_ID);
  
  // En servidor, siempre permitir
  if (!isPlatformBrowser(platformId)) {
    return true;
  }

  // En browser, usar Promise para diferir la validación
  const jwtService = inject(JwtService);
  const router = inject(Router);

  return new Promise<boolean>((resolve) => {
    // Pequeño delay para asegurar que la hidratación esté completa
    setTimeout(() => {
      
      if (jwtService.isAuthenticated()) {
        resolve(checkRouteAccess(state.url, jwtService, router));
      } else {
        router.navigate(['/login']);
        resolve(false);
      }
    }, 50); // 50ms delay
  });
};

/**
 * ✅ GUARD HÍBRIDO CON FALLBACK
 * Mejor opción para la mayoría de casos
 */
export const hybridAuthGuard: CanActivateFn = (route, state) => {
  const platformId = inject(PLATFORM_ID);
  const jwtService = inject(JwtService);
  const router = inject(Router);


  // ESTRATEGIA SSR: Permitir navegación inicial
  if (!isPlatformBrowser(platformId)) {
    
    // Para rutas críticas, podrías hacer verificaciones del lado del servidor
    // Por ejemplo, validar JWT con el backend directamente
    return true;
  }

  // ESTRATEGIA BROWSER: Verificación completa después de hidratación
  
  // Verificar que el localStorage esté disponible
  if (typeof localStorage === 'undefined') {
    return true;
  }

  // Verificación normal
  if (!jwtService.isAuthenticated()) {
    router.navigate(['/login']);
    return false;
  }

  return checkRouteAccess(state.url, jwtService, router);
};

// ============================================
// ✅ GUARDS ESPECÍFICOS SIN CAMBIOS SSR
// ============================================

export const superadminGuard: CanActivateFn = (route, state) => {
  const platformId = inject(PLATFORM_ID);
  
  if (!isPlatformBrowser(platformId)) {
    return true; // Permitir en SSR
  }
  
  const jwtService = inject(JwtService);
  const router = inject(Router);

  if (!jwtService.isAuthenticated()) {
    router.navigate(['/login']);
    return false;
  }

  const payload = jwtService.decodeToken();
  
  if (payload?.is_superuser) {
    return true;
  } else {
    router.navigate(['/fs/home']);
    return false;
  }
};

export function moduleGuard(moduleName: string, tipo: 'web' | 'movil' = 'web'): CanActivateFn {
  return (route, state) => {
    const platformId = inject(PLATFORM_ID);
    
    if (!isPlatformBrowser(platformId)) {
      return true; // Permitir en SSR
    }
    
    const jwtService = inject(JwtService);
    const router = inject(Router);

    if (!jwtService.isAuthenticated()) {
      router.navigate(['/login']);
      return false;
    }

    if (jwtService.canAccessModule(moduleName, tipo)) {
      return true;
    } else {
      router.navigate(['/fs/home']);
      return false;
    }
  };
}

export function submoduleGuard(moduleName: string, submoduleName: string, tipo: 'web' | 'movil' = 'web'): CanActivateFn {
  return (route, state) => {
    const platformId = inject(PLATFORM_ID);
    
    if (!isPlatformBrowser(platformId)) {
      return true; // Permitir en SSR
    }
    
    const jwtService = inject(JwtService);
    const router = inject(Router);

    if (!jwtService.isAuthenticated()) {
      router.navigate(['/login']);
      return false;
    }

    if (jwtService.canAccessSubmodule(moduleName, submoduleName, tipo)) {
      return true;
    } else {
      router.navigate(['/fs/home']);
      return false;
    }
  };
}

export function permissionGuard(requiredPermissions: string[]): CanActivateFn {
  return (route, state) => {
    const platformId = inject(PLATFORM_ID);
    
    if (!isPlatformBrowser(platformId)) {
      return true; // Permitir en SSR
    }
    
    const jwtService = inject(JwtService);
    const router = inject(Router);

    if (!jwtService.isAuthenticated()) {
      router.navigate(['/login']);
      return false;
    }

    const payload = jwtService.decodeToken();
    if (!payload) {
      router.navigate(['/login']);
      return false;
    }

    if (payload.is_superuser) {
      return true;
    }

    const hasWebModules = payload.permissions.web && Object.keys(payload.permissions.web).length > 0;
    const hasMovilModules = payload.permissions.movil && Object.keys(payload.permissions.movil).length > 0;

    if (hasWebModules || hasMovilModules) {
      return true;
    } else {
      router.navigate(['/fs/home']);
      return false;
    }
  };
}