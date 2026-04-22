import { HttpClient, HttpParams } from '@angular/common/http';
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

  getAtribuicoes(page: number = 1, limit: number = 100, filters: any = {}): Observable<any> {
    // Calculamos o 'skip' exato que o FastAPI espera
    const skip = (page - 1) * limit;

    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    // Injetar filtros (ex: escola_id, professor_id, ano_letivo)
    if (filters) {
        Object.keys(filters).forEach(key => {
            if (filters[key] !== null && filters[key] !== undefined && filters[key] !== '') {
                params = params.set(key, filters[key].toString());
            }
        });
    }

    // A barra final "/" evita o erro 307 Temporary Redirect no FastAPI
    return this.http.get<any>(`${this.apiUrl}/`, { params });
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

  // ✅ Método para obter as aulas do professor logado
  getMinhasAulas(professor_id: number): Observable<any[]> {
    // return this.http.get<any[]>(`${this.apiUrl}/horarios/minhas-aulas`);
    return this.http.get<any[]>(`${this.apiUrl}/professor/${professor_id}`);
  }

  getMinhasTurmas(professor_id: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/horarios/minhas-turmas`, {
      params: new HttpParams().set('professor_id', professor_id.toString())
    });
  }
}
