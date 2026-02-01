import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface Mensalidade {
  id: number;
  descricao: string; // Ex: "Mensalidade - Setembro 2024"
  mes: string;
  ano: number;
  valor_base: number;
  data_vencimento: string; // Nova data limite
  estado: string; // 'Pendente', 'Pago', 'Atrasado', 'Cancelado'
  data_pagamento?: string;
  forma_pagamento?: string;
  aluno_id: number;
  pago_por_id?: number; // Auditoria: quem recebeu o dinheiro
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

  // 2. Gera o carnet anual (Agora é Inteligente e usa os dados do Backend)
  gerarCarnet(alunoId: number, ano: number): Observable<Mensalidade[]> {
    return this.http.post<Mensalidade[]>(
      `${this.apiUrl}/alunos/${alunoId}/financeiro/gerar?ano=${ano}`,
      {}
    );
  }

  // 3. Pagar uma mensalidade
  pagar(mensalidadeId: number, dados: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/financeiro/${mensalidadeId}/pagar`, dados);
  }

  // 4. Buscar Recibo Único
  getMensalidadeById(id: number): Observable<Mensalidade> {
    return this.http.get<Mensalidade>(`${this.apiUrl}/financeiro/${id}`);
  }
}
