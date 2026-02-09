import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Disciplina } from './disciplina.service';
import { environment } from '../../environments/environment.development';

export interface Turma {
  id?: number;
  nome: string;       // Ex: "10ª A"
  ano_letivo: string; // Ex: "2024"
  turno?: string;     // Ex: "Manhã"
  escola_id: number;
  disciplinas?: Disciplina[];
}

@Injectable({
  providedIn: 'root'
})
export class TurmaService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  constructor() { }

  criarTurma(turma: Turma): Observable<Turma> {
    return this.http.post<Turma>(`${this.apiUrl}/turmas/`, turma);
  }

  // Método para obter turmas, com opção de filtrar por escola
  getTurmas(escolaId?: number): Observable<Turma[]> {
    if (escolaId) {
      // Se escolaId foi fornecido, busca as turmas dessa escola específica
      return this.http.get<Turma[]>(`${this.apiUrl}/escolas/${escolaId}/turmas`);
    } else {
      // Se não foi fornecido, busca as turmas da escola do usuário logado
      return this.http.get<Turma[]>(`${this.apiUrl}/turmas/`);
    }
  }

  getTurmaById(id: number): Observable<Turma> {
    return this.http.get<Turma>(`${this.apiUrl}/turmas/${id}`);
  }

  // Métodos para Disciplinas
  // addDisciplina(disciplina: Disciplina): Observable<Disciplina> {
  //   return this.http.post<Disciplina>(`${this.apiUrl}/disciplinas/`, disciplina);
  // }

  getDisciplinasByTurma(turmaId: number): Observable<Disciplina[]> {
    return this.http.get<Disciplina[]>(`${this.apiUrl}/turmas/${turmaId}/disciplinas`);
  }

  // Método para associar disciplina a turma
  associarDisciplina(turmaId: number, disciplinaId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/turmas/${turmaId}/associar-disciplina/${disciplinaId}`, {});
  }

  // Metodo desassociar disciplina da turma

  desassociarDisciplina(turmaId: number, disciplinaId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/turmas/${turmaId}/remover-disciplina/${disciplinaId}`);
  }
}
