// frontend/src/app/core/services/crypto.service.ts - NOVO ARQUIVO
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class CryptoService {

  private readonly SECRET_KEY = 'sua-chave-secreta-fixa-aqui';  // Em produção, gerar dinamicamente

  /**
   * Criptografia simples XOR
   * NOTA: Para produção, usar biblioteca como crypto-js
   */
  encrypt(text: string): string {
    let encrypted = '';
    for (let i = 0; i < text.length; i++) {
      encrypted += String.fromCharCode(
        text.charCodeAt(i) ^ this.SECRET_KEY.charCodeAt(i % this.SECRET_KEY.length)
      );
    }
    return btoa(encrypted);
  }

  decrypt(encrypted: string): string {
    const decoded = atob(encrypted);
    let decrypted = '';
    for (let i = 0; i < decoded.length; i++) {
      decrypted += String.fromCharCode(
        decoded.charCodeAt(i) ^ this.SECRET_KEY.charCodeAt(i % this.SECRET_KEY.length)
      );
    }
    return decrypted;
  }
}
