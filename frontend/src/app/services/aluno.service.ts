import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface Aluno {
  id?: number;
  nome: string;
  bi?: string;
  data_nascimento?: string;
  escola_id: number;
  ativo?: boolean;     // <--- Adicionei isto para mostrar na tabela
  created_at?: string; // <--- Adicionei isto para mostrar a data
}

@Injectable({
  providedIn: 'root',
})
export class AlunoService {
  private http = inject(HttpClient);
  private apiUrl = 'http://127.0.0.1:8000';

  constructor() { }

  matricularAluno(aluno: Aluno): Observable<Aluno> {
    return this.http.post<Aluno>(`${this.apiUrl}/alunos/`, aluno);
  }

  getAlunos(escolaId: number): Observable<Aluno[]> {
    return this.http.get<Aluno[]>(`${this.apiUrl}/escolas/${escolaId}/alunos`);
  }

  getAlunoById(id: number): Observable<Aluno> {
    return this.http.get<Aluno>(`${this.apiUrl}/alunos/${id}`);
  }

  atualizarAluno(id: number, aluno: Partial<Aluno>): Observable<Aluno> {
    return this.http.put<Aluno>(`${this.apiUrl}/alunos/${id}`, aluno);
  }

  removerAluno(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/alunos/${id}`);
  }
}
