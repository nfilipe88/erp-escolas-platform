import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment.development';
import { Role } from './role.service';

export interface Usuario {
  id?: number;
  nome: string;
  email: string;
  ativo: boolean;
  escola_id?: number | null;
  roles: Role[];
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private apiUrl = environment.apiUrl;

  currentUser = signal<any>(null);

  constructor() {
    this.verificarLogin();
  }

  login(email: string, senha: string): Observable<any> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', senha);

    return this.http.post<any>(`${this.apiUrl}/auth/login`, formData).pipe(
      tap(response => {
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
        localStorage.setItem('user_nome', response.nome);
        // Guardar as roles em JSON
        localStorage.setItem('user_roles', JSON.stringify(response.roles));
        if (response.escola_id) {
          localStorage.setItem('user_escola_id', response.escola_id.toString());
        } else {
          localStorage.removeItem('user_escola_id');
        }

        this.currentUser.set({
          nome: response.nome,
          roles: response.roles,
          escola_id: response.escola_id
        } as Usuario);
      })
    );
  }

  // --- CORREÇÃO: Método em falta para o Interceptor ---
  refreshToken(token: string): Observable<any> {
    // O backend espera query param: /auth/refresh?refresh_token=...
    return this.http.post<any>(`${this.apiUrl}/auth/refresh?refresh_token=${token}`, {}).pipe(
      tap(response => {
         localStorage.setItem('access_token', response.access_token);
         // Se vier um novo refresh token, atualiza também
         if (response.refresh_token) {
            localStorage.setItem('refresh_token', response.refresh_token);
         }
      })
    );
  }

  getUsuarioLogado(): Usuario | null {
    const nome = localStorage.getItem('user_nome');
    const rolesJson = localStorage.getItem('user_roles');
    const escolaId = localStorage.getItem('user_escola_id');

    if (nome && rolesJson) {
      try {
        const roles = JSON.parse(rolesJson);
        return {
          nome,
          roles,
          escola_id: escolaId ? parseInt(escolaId, 10) : null
        } as Usuario;
      } catch {
        return null;
      }
    }
    return null;
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token'); // Limpar refresh
    localStorage.removeItem('user_nome');
    localStorage.removeItem('user_perfil');
    localStorage.removeItem('user_escola_id');
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  verificarLogin() {
    const token = localStorage.getItem('access_token');
    const user = this.getUsuarioLogado();
    if (token && user) {
      this.currentUser.set(user);
    }
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  alterarSenha(senhaAtual: string, novaSenha: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/auth/me/alterar-senha`, {
      senha_atual: senhaAtual,
      nova_senha: novaSenha
    });
  }

  esqueciSenha(email: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/esqueci-senha`, { email });
  }

  resetSenha(token: string, novaSenha: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/reset-senha`, {
      token: token,
      nova_senha: novaSenha
    });
  }
}
