import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface PresencaItem {
  aluno_id: number;
  presente: boolean;
  justificado: boolean;
  observacao?: string;
  // Campos auxiliares para a tela (nomes)
  aluno_nome?: string;
}

export interface ChamadaDiaria {
  turma_id: number;
  data: string; // Formato YYYY-MM-DD
  lista_alunos: PresencaItem[];
}

@Injectable({
  providedIn: 'root'
})
export class PresencaService {
  private http = inject(HttpClient);
  private apiUrl = 'http://127.0.0.1:8000';

  // 1. Salvar a chamada
  salvarChamada(dados: ChamadaDiaria): Observable<any> {
    return this.http.post(`${this.apiUrl}/presencas/`, dados);
  }

  // 2. Ler a chamada de um dia (para ver se já foi feita)
  lerChamada(turmaId: number, data: string): Observable<PresencaItem[]> {
    return this.http.get<PresencaItem[]>(`${this.apiUrl}/presencas/turma/${turmaId}?data=${data}`);
  }

  registar(payload: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/presencas/`, payload);
  }

  consultar(turmaId: number, data: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/presencas/${turmaId}/${data}`);
  }
}
