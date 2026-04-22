import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment.development';

export interface Aluno {
  id?: number;
  nome: string;
  bi?: string;
  data_nascimento?: string;
  escola_id?: number;
  turma_id?: number;
  ativo?: boolean;
  // Campos extra para listagem
  turma?: { id: number; nome: string };
  escola?: { id: number; nome: string };
}

// --- INTERFACE PARA PAGINAÇÃO ---
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface Boletim {
  aluno_nome: string;
  aluno_bi: string;
  escola_nome: string;
  ano_letivo?: string;
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

  // --- CORREÇÃO: Suporte a paginação e filtros para o NGRX ---
  getAlunos(page: number = 1, limit: number = 10, filters: any = {}): Observable<PaginatedResponse<Aluno>> {
    // Calculamos o 'skip' para o backend (que usa skip e limit)
    const skip = (page - 1) * limit;

    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    // Anexamos apenas os filtros que não sejam nulos, indefinidos ou vazios
    if (filters) {
        Object.keys(filters).forEach(key => {
            if (filters[key] !== null && filters[key] !== undefined && filters[key] !== '') {
                params = params.set(key, filters[key].toString());
            }
        });
    }

    return this.http.get<PaginatedResponse<Aluno>>(`${this.apiUrl}`, { params });
  }

  createAluno(aluno: Aluno): Observable<Aluno> {
    return this.matricularAluno(aluno);
  }

  getAlunoById(id: number): Observable<Aluno> {
    return this.http.get<Aluno>(`${this.apiUrl}/alunos/${id}`);
  }

  updateAluno(id: number, aluno: Partial<Aluno>): Observable<Aluno> {
    return this.atualizarAluno(id, aluno);
  }

  deleteAluno(id: number): Observable<any> {
    return this.removerAluno(id);
  }

  // Manter compatibilidade com métodos antigos se necessário
  atualizarAluno(id: number, aluno: Partial<Aluno>): Observable<Aluno> {
    return this.http.put<Aluno>(`${this.apiUrl}/alunos/${id}`, aluno);
  }

  removerAluno(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/alunos/${id}`);
  }

  getAlunosPorTurma(turmaId: number): Observable<Aluno[]> {
    return this.http.get<Aluno[]>(`${this.apiUrl}/alunos/turma/${turmaId}`);
  }

  getBoletim(alunoId: number): Observable<Boletim> {
    return this.http.get<Boletim>(`${this.apiUrl}/alunos/${alunoId}/boletim`);
  }
}
