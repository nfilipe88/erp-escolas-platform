import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core'; // Usaremos signals para reatividade
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private apiUrl = 'http://127.0.0.1:8000';

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
        console.log('Resposta do login:', response); // DEBUG
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('user_nome', response.nome);
        localStorage.setItem('user_perfil', response.perfil);
        localStorage.setItem('user_escola_id', response.escola_id);

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
    const escola_id = localStorage.getItem('user_escola_id');

    if (nome && perfil) {
      return {
        nome,
        perfil,
        escola_id: escola_id ? parseInt(escola_id) : null
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
    const nome = localStorage.getItem('user_nome');
    if (token && nome) {
      this.currentUser.set({ nome: nome });
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

  // Pedir o email
  esqueciSenha(email: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/esqueci-senha`, { email });
  }

  // Enviar a nova senha com o token
  resetSenha(token: string, novaSenha: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/reset-senha`, {
      token: token,
      nova_senha: novaSenha
    });
  }
}
