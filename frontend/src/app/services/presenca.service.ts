import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment.development';

export interface PresencaItem {
  aluno_id: number;
  presente: boolean;
  justificado: boolean;
  observacao?: string;
  aluno_nome?: string;
}

export interface ChamadaDiaria {
  turma_id: number;
  data: string;
  lista_alunos: PresencaItem[];
}

@Injectable({ providedIn: 'root' })
export class PresencaService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  // ✅ CORRIGIDO: endpoint correto é /presencas/chamada
  registarChamada(chamada: ChamadaDiaria): Observable<any> {
    return this.http.post(`${this.apiUrl}/`, chamada);
  }

  // ✅ CORRIGIDO: GET /presencas/chamada/{turma_id}/{data}
  consultarChamada(turmaId: number, data: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${turmaId}/${data}`);
  }

  getPresencas(page: number = 1, limit: number = 100, filters: any = {}): Observable<any> {
    const skip = (page - 1) * limit;
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    if (filters) {
        Object.keys(filters).forEach(key => {
            if (filters[key] !== null && filters[key] !== undefined && filters[key] !== '') {
                // Muito útil para filtrar pela "data" e "turma_id" específicas do dia da chamada
                params = params.set(key, filters[key].toString());
            }
        });
    }

    return this.http.get<any>(`${this.apiUrl}/`, { params });
  }

  // O professor marca a falta do aluno
  createPresenca(presenca: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/`, presenca);
  }

  // --- Ponto dos Professores (com prefixo /presencas) ---
  getPontoProfessores(data: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${data}`);
  }

  salvarPontoProfessores(payload: { data: string; lista: any[] }): Observable<any> {
    return this.http.post(`${this.apiUrl}/`, payload);
  }
}
