import { HttpClient } from '@angular/common/http';
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
    return this.http.post(`${this.apiUrl}/presencas/chamada`, chamada);
  }

  // ✅ CORRIGIDO: GET /presencas/chamada/{turma_id}/{data}
  consultarChamada(turmaId: number, data: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/presencas/chamada/${turmaId}/${data}`);
  }

  // ❌ REMOVIDO: método lerChamada (redundante)

  // --- Ponto dos Professores (com prefixo /presencas) ---
  getPontoProfessores(data: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/presencas/ponto-professores/${data}`);
  }

  salvarPontoProfessores(payload: { data: string; lista: any[] }): Observable<any> {
    return this.http.post(`${this.apiUrl}/presencas/ponto-professores/`, payload);
  }
}
