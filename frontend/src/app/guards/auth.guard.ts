import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // 1. Verifica se está logado
  if (authService.isLoggedIn()) {
    return true; // Pode passar! ✅
  } else {
    // 2. Se não, manda para o login
    router.navigate(['/login']);
    return false; // Barrado! ⛔
  }
};
