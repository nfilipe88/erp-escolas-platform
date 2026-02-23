import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment.development';
import { Role } from './role.service';

export interface Usuario {
  id?: number;
  nome: string;
  email: string;
  senha?: string;
  roles: Role[];  // ← IDs das roles
  escola_id?: number | null;
  ativo: boolean;
}

export interface UsuarioCreate {
  nome: string;
  email: string;
  senha: string;
  roles: number[]; // ← apenas IDs (payload)
  escola_id?: number | null;
  ativo: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class UsuarioService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  getUsuarios(): Observable<Usuario[]> {
    return this.http.get<Usuario[]>(`${this.apiUrl}/usuarios/`);
  }

  createUsuario(usuario: UsuarioCreate): Observable<Usuario> {
    return this.http.post<Usuario>(`${this.apiUrl}/usuarios/`, usuario);
  }

  // Opcional: Implementar Delete/Update depois
}
