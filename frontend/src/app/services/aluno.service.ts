import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment.development';

export interface Aluno {
  id?: number;
  nome: string;
  bi?: string;
  data_nascimento?: string;
  escola_id?: number;   // ← AGORA OPCIONAL (só superadmin envia)
  turma_id?: number;
  ativo?: boolean;
}

export interface Boletim {
  aluno_nome: string;
  aluno_bi: string;
  escola_nome: string;
  ano_letivo: string;
  turma: string;
  linhas: {
    disciplina: string;
    media_provisoria: number;
    notas: {
      trimestre: string;
      valor: number | null;
      descricao: string;
    }[];
  }[];
}

@Injectable({ providedIn: 'root' })
export class AlunoService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

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

  getAlunosPorTurma(turmaId: number): Observable<Aluno[]> {
    return this.http.get<Aluno[]>(`${this.apiUrl}/turmas/${turmaId}/alunos`);
  }

  getBoletim(alunoId: number): Observable<Boletim> {
    return this.http.get<Boletim>(`${this.apiUrl}/alunos/${alunoId}/boletim`);
  }
}
