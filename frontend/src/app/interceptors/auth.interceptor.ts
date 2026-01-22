import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
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
        localStorage.removeItem('user_name');
        localStorage.removeItem('user_perfil');

        // Redireciona para o login
        router.navigate(['/login']);
      }

      return throwError(() => error);
    })
  );
};
