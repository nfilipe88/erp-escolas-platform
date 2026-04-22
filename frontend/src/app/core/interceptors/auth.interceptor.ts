import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpEvent } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, filter, take } from 'rxjs/operators';
import { throwError, BehaviorSubject, Observable } from 'rxjs';
import { AuthService } from '../../services/auth.service';

let isRefreshing = false;
let refreshTokenSubject: BehaviorSubject<string | null> = new BehaviorSubject<string | null>(null);

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);

  // 1. Lemos diretamente do localStorage, em sincronia perfeita com o AuthService
  const token = localStorage.getItem('access_token');

  let clonedReq = req;
  if (token) {
    clonedReq = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    });
  }

  return next(clonedReq).pipe(
    catchError(error => {
      if (error.status === 401) {
        return handle401Error(clonedReq, next, authService);
      }
      return throwError(() => error);
    })
  );
};

// Mantemos as tipagens estritas para evitar o erro TS2322
function handle401Error(
  request: HttpRequest<unknown>,
  next: HttpHandlerFn,
  authService: AuthService
): Observable<HttpEvent<unknown>> {

  if (!isRefreshing) {
    isRefreshing = true;
    refreshTokenSubject.next(null);

    // 2. Lemos o refresh token do localStorage
    const refreshToken = localStorage.getItem('refresh_token');

    if (refreshToken) {
      return authService.refreshToken(refreshToken).pipe(
        switchMap((response: any) => {
          isRefreshing = false;
          // O AuthService já guardou o novo token, só precisamos de avisar os pedidos pendentes
          refreshTokenSubject.next(response.access_token);

          const newRequest = request.clone({
            setHeaders: { Authorization: `Bearer ${response.access_token}` }
          });
          return next(newRequest);
        }),
        catchError(err => {
          isRefreshing = false;
          authService.logout();
          return throwError(() => err);
        })
      );
    } else {
        isRefreshing = false;
        authService.logout();
    }
  }

  return refreshTokenSubject.pipe(
    filter(token => token !== null),
    take(1),
    switchMap(token => {
      const newRequest = request.clone({
        setHeaders: { Authorization: `Bearer ${token}` }
      });
      return next(newRequest);
    })
  );
}
