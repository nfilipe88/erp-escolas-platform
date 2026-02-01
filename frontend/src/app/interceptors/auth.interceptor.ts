import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // const router = inject(Router);
  const authService = inject(AuthService);
  const token = localStorage.getItem('access_token');

  // Clona o pedido se houver token
  let request = req;
  if (token) {
    request = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    });
  }

  // Envia o pedido e fica à escuta de erros
  return next(request).pipe(
    catchError((error: HttpErrorResponse) => {

      // Se o erro for 401 (Não Autorizado / Token Expirado)
      if (error.status === 401) {
        // Limpa o armazenamento
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_nome');
        localStorage.removeItem('user_perfil');
        console.warn("Sessão expirada. A fechar a aplicação...");

        // ISTO FAZ A MAGIA: Limpa o storage, o Signal (esconde o menu) e vai para o Login
        authService.logout();
      }

      return throwError(() => error);
    })
  );
};
