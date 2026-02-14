import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment.development';

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
        localStorage.setItem('user_nome', response.nome);
        localStorage.setItem('user_perfil', response.perfil);
        // ✅ Guarda 'null' como string e trata na leitura
        localStorage.setItem('user_escola_id', response.escola_id ?? 'null');

        this.currentUser.set({
          nome: response.nome,
          perfil: response.perfil,
          escola_id: response.escola_id
        });
      })
    );
  }

  getUsuarioLogado() {
    const nome = localStorage.getItem('user_nome');
    const perfil = localStorage.getItem('user_perfil');
    const escolaId = localStorage.getItem('user_escola_id');

    if (nome && perfil) {
      return {
        nome,
        perfil,
        // ✅ Trata 'null' / 'undefined' / vazio
        escola_id: escolaId && escolaId !== 'null' && escolaId !== 'undefined'
          ? parseInt(escolaId, 10)
          : null
      };
    }
    return null;
  }

  logout() {
    localStorage.removeItem('access_token');
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
