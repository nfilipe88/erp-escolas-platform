import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface Turma {
  id?: number;
  nome: string;       // Ex: "10ª A"
  ano_letivo: string; // Ex: "2024"
  turno?: string;     // Ex: "Manhã"
  escola_id: number;
}

@Injectable({
  providedIn: 'root'
})
export class TurmaService {
  private http = inject(HttpClient);
  private apiUrl = 'http://127.0.0.1:8000';

  constructor() { }

  criarTurma(turma: Turma): Observable<Turma> {
    return this.http.post<Turma>(`${this.apiUrl}/turmas/`, turma);
  }

  getTurmas(escolaId: number): Observable<Turma[]> {
    return this.http.get<Turma[]>(`${this.apiUrl}/escolas/${escolaId}/turmas`);
  }
}
