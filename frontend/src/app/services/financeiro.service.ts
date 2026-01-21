import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface Mensalidade {
  id: number;
  mes: string;
  ano: number;
  valor_base: number;
  estado: string;         // 'Pendente' | 'Pago'
  data_pagamento?: string;
  forma_pagamento?: string;
  aluno_id: number;
}

@Injectable({
  providedIn: 'root',
})
export class FinanceiroService {
  private http = inject(HttpClient);
  private apiUrl = 'http://127.0.0.1:8000';

  // 1. Busca o extrato do aluno
  getMensalidades(alunoId: number): Observable<Mensalidade[]> {
    return this.http.get<Mensalidade[]>(`${this.apiUrl}/alunos/${alunoId}/financeiro`);
  }

  // 2. Gera o carnet anual (Cria a dívida)
  gerarCarnet(alunoId: number, ano: number): Observable<Mensalidade[]> {
    // Post vazio ou com parâmetros se quiseres mudar o valor
    return this.http.post<Mensalidade[]>(
      `${this.apiUrl}/alunos/${alunoId}/financeiro/gerar?ano=${ano}&valor=15000`,
      {}
    );
  }

  // 3. Pagar uma mensalidade
  pagar(mensalidadeId: number, forma: string): Observable<Mensalidade> {
    const payload = {
      data_pagamento: new Date().toISOString().split('T')[0], // Hoje: "2025-01-22"
      forma_pagamento: forma
    };
    return this.http.put<Mensalidade>(`${this.apiUrl}/financeiro/${mensalidadeId}/pagar`, payload);
  }

  // 4. Buscar detalhes de um pagamento específico (para o recibo)
  getMensalidadeById(id: number): Observable<Mensalidade> {
    return this.http.get<Mensalidade>(`${this.apiUrl}/financeiro/${id}`);
  }
}
