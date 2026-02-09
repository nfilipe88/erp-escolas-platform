import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment.development';

export interface Nota {
  id?: number;
  valor: number;
  trimestre: string;
  descricao?: string;
  aluno_id: number;
  disciplina_id: number;
  arquivo_url?: string; // O link do PDF
}

@Injectable({
  providedIn: 'root',
})
export class NotaService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  constructor() { }

  // ⚠️ AQUI ESTÁ A MAGIA DO UPLOAD
  lancarNota(nota: any, arquivo?: File): Observable<Nota> {
    const formData = new FormData();

    // Adicionamos os campos de texto
    formData.append('aluno_id', nota.aluno_id);
    formData.append('disciplina_id', nota.disciplina_id);
    formData.append('valor', nota.valor);
    formData.append('trimestre', nota.trimestre);
    formData.append('descricao', nota.descricao || 'Prova');

    // Se houver ficheiro, anexamos ao pacote
    if (arquivo) {
      formData.append('arquivo', arquivo);
    }

    // O Angular deteta que é FormData e ajusta os cabeçalhos automaticamente
    return this.http.post<Nota>(`${this.apiUrl}/notas/`, formData);
  }

  getNotasPorDisciplina(disciplinaId: number): Observable<Nota[]> {
    return this.http.get<Nota[]>(`${this.apiUrl}/disciplinas/${disciplinaId}/notas`);
  }
}
