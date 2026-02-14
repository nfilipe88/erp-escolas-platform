import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment.development';

export interface Mensalidade {
  id: number;
  descricao: string;
  mes: string;
  ano: number;
  valor_base: number;
  data_vencimento: string;
  estado: string;
  data_pagamento?: string;
  forma_pagamento?: string;
  aluno_id: number;
  pago_por_id?: number;
}

@Injectable({ providedIn: 'root' })
export class FinanceiroService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  // ✅ CORRIGIDO
  getMensalidades(alunoId: number): Observable<Mensalidade[]> {
    return this.http.get<Mensalidade[]>(`${this.apiUrl}/financeiro/aluno/${alunoId}`);
  }

  // ✅ CORRIGIDO
  gerarCarnet(alunoId: number, ano: number): Observable<Mensalidade[]> {
    return this.http.post<Mensalidade[]>(
      `${this.apiUrl}/financeiro/gerar-carnet/${alunoId}?ano=${ano}`,
      {}
    );
  }

  // ✅ CORRETO
  pagar(mensalidadeId: number, dados: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/financeiro/${mensalidadeId}/pagar`, dados);
  }

  // ✅ CORRETO
  getMensalidadeById(id: number): Observable<Mensalidade> {
    return this.http.get<Mensalidade>(`${this.apiUrl}/financeiro/${id}`);
  }

  // ✅ CORRIGIDO (relatórios)
  getResumoFinanceiro(): Observable<any> {
    return this.http.get(`${this.apiUrl}/financeiro/relatorios/resumo`);
  }

  getFluxoCaixa(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/financeiro/relatorios/fluxo`);
  }

  getDevedores(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/financeiro/relatorios/devedores`);
  }
}
