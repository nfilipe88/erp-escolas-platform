import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment.development';

export interface Atribuicao {
  id: number;
  turma_id: number;
  disciplina_id: number;
  professor_id: number;
  turma_nome: string;
  disciplina_nome: string;
  professor_nome: string;
}

// ✅ Permite null (para o formulário)
export interface AtribuicaoCreate {
  escola_id?: number;
  turma_id: number | null;
  disciplina_id: number | null;
  professor_id: number | null;
}

@Injectable({ providedIn: 'root' })
export class AtribuicaoService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  getAtribuicoes(): Observable<Atribuicao[]> {
    return this.http.get<Atribuicao[]>(`${this.apiUrl}/atribuicoes/`);
  }

  criar(dados: AtribuicaoCreate): Observable<Atribuicao> {
    return this.http.post<Atribuicao>(`${this.apiUrl}/atribuicoes/`, dados);
  }

  remover(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/atribuicoes/${id}`);
  }

  getProfessores(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/usuarios/professores`);
  }

  getMinhasAulas(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/horarios/minhas-aulas`);
  }
}
