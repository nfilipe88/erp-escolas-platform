import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

// Definimos o tipo de dados que esperamos (igual ao Schema do Python)
export interface Escola {
  id?: number;
  nome: string;
  slug: string;
  endereco?: string;
  telefone?: string; // Adicionado
  email?: string;    // Adicionado
  is_ative:boolean;
}

// --- NOVA INTERFACE ---
export interface ConfiguracaoEscola {
  id?: number;
  escola_id?: number;
  valor_mensalidade_padrao: number;
  dia_vencimento: number;
  multa_atraso_percentual: number;
  desconto_pagamento_anual: number;
  mes_inicio_cobranca: number;
  mes_fim_cobranca: number;
  bloquear_boletim_devedor: boolean;
  nota_minima_aprovacao: number;
}

export interface EscolaDetalhes extends Escola { // Herda nome, slug, etc.
  total_alunos: number;
  alunos_ativos: number;
  alunos_inativos: number;
  total_turmas: number;
  total_usuarios: number;
  contagem_por_perfil: { [key: string]: number }; // Dicionário { 'professor': 10 }
  // CORREÇÃO AQUI: Adicionámos 'id' e 'perfil'
  lista_diretores: Array<{
    id: number;
    nome: string;
    email: string;
    perfil?: string;
  }>;
  created_at: string;
}

@Injectable({
  providedIn: 'root',
})
export class EscolaService {
  private http = inject(HttpClient);
  private apiUrl = 'http://127.0.0.1:8000'; // O endereço do teu Python

  constructor() { }

  getEscolas(): Observable<Escola[]> {
    return this.http.get<Escola[]>(`${this.apiUrl}/escolas/`);
  }

  getEscolaDetalhes(id: number): Observable<EscolaDetalhes> {
    return this.http.get<EscolaDetalhes>(`${this.apiUrl}/escolas/${id}/detalhes`);
  }

  // Função para enviar os dados para o Backend
  criarEscola(escola: Escola): Observable<Escola> {
    return this.http.post<Escola>(`${this.apiUrl}/escolas/`, escola);
  }

  // --- NOVOS MÉTODOS DE CONFIGURAÇÃO (SaaS) ---
  getConfiguracao(): Observable<ConfiguracaoEscola> {
    return this.http.get<ConfiguracaoEscola>(`${this.apiUrl}/minha-escola/configuracoes`);
  }

  updateConfiguracao(dados: ConfiguracaoEscola): Observable<ConfiguracaoEscola> {
    return this.http.put<ConfiguracaoEscola>(`${this.apiUrl}/minha-escola/configuracoes`, dados);
  }
}
