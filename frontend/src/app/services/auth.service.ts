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

  // Signal para saber se está logado (Atualiza a UI automaticamente)
  currentUser = signal<any>(null);

  constructor() {
    // Ao iniciar, verifica se já existe token guardado
    this.verificarLogin();
  }

  login(email: string, senha: string): Observable<any> {
    const formData = new FormData();
    formData.append('username', email); // O FastAPI espera 'username' por padrão
    formData.append('password', senha);

    return this.http.post<any>(`${this.apiUrl}/auth/login`, formData).pipe(
      tap(response => {
        // 1. Guardar o Token no navegador
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('user_name', response.nome);

        // 2. Atualizar o estado da aplicação
        this.currentUser.set({ nome: response.nome, perfil: response.perfil });
      })
    );
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_name');
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  verificarLogin() {
    const token = localStorage.getItem('access_token');
    const nome = localStorage.getItem('user_name');
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
