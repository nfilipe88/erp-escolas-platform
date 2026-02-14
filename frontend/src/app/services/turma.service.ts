import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Disciplina } from './disciplina.service';
import { environment } from '../../environments/environment.development';

export interface Turma {
  id?: number;
  nome: string;
  ano_letivo: string;
  turno?: string;
  escola_id?: number;   // ← ADICIONADO (opcional, só para superadmin)
  disciplinas?: Disciplina[];
}

@Injectable({ providedIn: 'root' })
export class TurmaService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  criarTurma(turma: Turma): Observable<Turma> {
    return this.http.post<Turma>(`${this.apiUrl}/turmas/`, turma);
  }

  getTurmas(escolaId?: number): Observable<Turma[]> {
    if (escolaId) {
      return this.http.get<Turma[]>(`${this.apiUrl}/escolas/${escolaId}/turmas`);
    }
    return this.http.get<Turma[]>(`${this.apiUrl}/turmas/`);
  }

  getTurmaById(id: number): Observable<Turma> {
    return this.http.get<Turma>(`${this.apiUrl}/turmas/${id}`);
  }

  getDisciplinasByTurma(turmaId: number): Observable<Disciplina[]> {
    return this.http.get<Disciplina[]>(`${this.apiUrl}/turmas/${turmaId}/disciplinas`);
  }

  // ✅ ROTAS CORRIGIDAS (alinhadas com o backend)
  associarDisciplina(turmaId: number, disciplinaId: number): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/turmas/${turmaId}/disciplinas/${disciplinaId}`,
      {}
    );
  }

  desassociarDisciplina(turmaId: number, disciplinaId: number): Observable<any> {
    return this.http.delete(
      `${this.apiUrl}/turmas/${turmaId}/disciplinas/${disciplinaId}`
    );
  }
}
