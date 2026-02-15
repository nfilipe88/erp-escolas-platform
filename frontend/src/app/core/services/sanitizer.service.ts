// frontend/src/app/core/services/sanitizer.service.ts - NOVO ARQUIVO
import { Injectable } from '@angular/core';
import { DomSanitizer, SafeHtml, SafeUrl, SafeResourceUrl } from '@angular/platform-browser';

@Injectable({
  providedIn: 'root'
})
export class SanitizerService {

  constructor(private domSanitizer: DomSanitizer) {}

  /**
   * Sanitizar HTML para prevenir XSS
   */
  sanitizeHtml(html: string): SafeHtml {
    return this.domSanitizer.sanitize(1, html) || '';
  }

  /**
   * Sanitizar URL
   */
  sanitizeUrl(url: string): SafeUrl {
    return this.domSanitizer.sanitize(4, url) || '';
  }

  /**
   * Escapar caracteres especiais HTML
   */
  escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Remover tags HTML de string
   */
  stripHtml(html: string): string {
    const tmp = document.createElement('DIV');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
  }

  /**
   * Validar e limpar entrada de usuário
   */
  cleanInput(input: string, maxLength: number = 255): string {
    if (!input) return '';

    // Remover caracteres de controle
    let cleaned = input.replace(/[\x00-\x1F\x7F-\x9F]/g, '');

    // Limitar tamanho
    cleaned = cleaned.substring(0, maxLength);

    // Trimmar espaços
    cleaned = cleaned.trim();

    return cleaned;
  }

  /**
   * Validar email
   */
  isValidEmail(email: string): boolean {
    const emailRegex = /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/i;
    return emailRegex.test(email);
  }

  /**
   * Validar BI (ajustar para formato de Angola)
   */
  isValidBI(bi: string): boolean {
    // Formato: 9 dígitos + 2 letras + 3 dígitos
    const biRegex = /^[0-9]{9}[A-Z]{2}[0-9]{3}$/;
    return biRegex.test(bi);
  }
}
