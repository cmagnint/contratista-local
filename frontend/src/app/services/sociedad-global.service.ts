import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SociedadGlobalService {
  // Sociedad seleccionada globalmente
  private sociedadSeleccionadaSubject = new BehaviorSubject<{ id: number; nombre: string } | null>(null);
  public sociedadSeleccionada$ = this.sociedadSeleccionadaSubject.asObservable();

  setSociedad(sociedad: { id: number; nombre: string }) {
    this.sociedadSeleccionadaSubject.next(sociedad);
    localStorage.setItem('sociedad_global', JSON.stringify(sociedad));
  }

  getSociedad(): { id: number; nombre: string } | null {
    return this.sociedadSeleccionadaSubject.value;
  }

  cargarSociedadGuardada(): void {
    const sociedadStr = localStorage.getItem('sociedad_global');
    if (sociedadStr) {
      this.sociedadSeleccionadaSubject.next(JSON.parse(sociedadStr));
    }
  }
}