// frontend/src/app/shared/pipes/safe-html.pipe.ts - NOVO ARQUIVO
import { Pipe, PipeTransform } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Pipe({
  name: 'safeHtml',
  standalone: true
})
export class SafeHtmlPipe implements PipeTransform {

  constructor(private sanitizer: DomSanitizer) {}

  transform(value: string): SafeHtml {
    // Apenas sanitizar, não permitir HTML arbitrário
    return this.sanitizer.sanitize(1, value) || '';
  }
}

// USO NOS COMPONENTES - EVITAR innerHTML
// ❌ INSEGURO:
// <div [innerHTML]="nomeAluno"></div>

// ✅ SEGURO:
// <div>{{ nomeAluno }}</div>
// OU se realmente precisar de HTML:
// <div [innerHTML]="nomeAluno | safeHtml"></div>
