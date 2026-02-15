// frontend/src/app/core/services/secure-storage.service.ts - NOVO ARQUIVO
import { Injectable } from '@angular/core';
import { CryptoService } from './crypto.service';

@Injectable({
  providedIn: 'root'
})
export class SecureStorageService {

  private readonly TOKEN_KEY = 'auth_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private readonly USER_KEY = 'user_data';

  constructor(private cryptoService: CryptoService) {}

  /**
   * Salvar token de forma segura
   * MELHOR PRÁTICA: usar httpOnly cookies no backend
   * Se precisar usar localStorage, criptografar
   */
  setToken(token: string): void {
    try {
      // Criptografar antes de salvar
      const encrypted = this.cryptoService.encrypt(token);
      sessionStorage.setItem(this.TOKEN_KEY, encrypted);
    } catch (error) {
      console.error('Erro ao salvar token:', error);
    }
  }

  getToken(): string | null {
    try {
      const encrypted = sessionStorage.getItem(this.TOKEN_KEY);
      if (!encrypted) return null;

      // Descriptografar
      return this.cryptoService.decrypt(encrypted);
    } catch (error) {
      console.error('Erro ao recuperar token:', error);
      return null;
    }
  }

  setRefreshToken(token: string): void {
    try {
      const encrypted = this.cryptoService.encrypt(token);
      // Refresh token pode usar localStorage (vida mais longa)
      localStorage.setItem(this.REFRESH_TOKEN_KEY, encrypted);
    } catch (error) {
      console.error('Erro ao salvar refresh token:', error);
    }
  }

  getRefreshToken(): string | null {
    try {
      const encrypted = localStorage.getItem(this.REFRESH_TOKEN_KEY);
      if (!encrypted) return null;

      return this.cryptoService.decrypt(encrypted);
    } catch (error) {
      console.error('Erro ao recuperar refresh token:', error);
      return null;
    }
  }

  setUser(user: any): void {
    try {
      const encrypted = this.cryptoService.encrypt(JSON.stringify(user));
      sessionStorage.setItem(this.USER_KEY, encrypted);
    } catch (error) {
      console.error('Erro ao salvar usuário:', error);
    }
  }

  getUser(): any | null {
    try {
      const encrypted = sessionStorage.getItem(this.USER_KEY);
      if (!encrypted) return null;

      const decrypted = this.cryptoService.decrypt(encrypted);
      return JSON.parse(decrypted);
    } catch (error) {
      console.error('Erro ao recuperar usuário:', error);
      return null;
    }
  }

  clearAll(): void {
    sessionStorage.removeItem(this.TOKEN_KEY);
    sessionStorage.removeItem(this.USER_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
  }

  /**
   * Verificar se token está expirado
   */
  isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp * 1000; // Converter para millisegundos
      return Date.now() >= exp;
    } catch {
      return true;
    }
  }
}
