import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface Atribuicao {
  id: number;
  turma_id: number;
  disciplina_id: number;
  professor_id: number;

  // Campos "bonitos" que vêm do Backend
  turma_nome: string;
  disciplina_nome: string;
  professor_nome: string;
}

export interface AtribuicaoCreate {
  turma_id: number;
  disciplina_id: number;
  professor_id: number;
}

@Injectable({
  providedIn: 'root'
})
export class AtribuicaoService {
  private http = inject(HttpClient);
  private apiUrl = 'http://127.0.0.1:8000';

  // 1. Listar todas as atribuições da escola
  getAtribuicoes(): Observable<Atribuicao[]> {
    return this.http.get<Atribuicao[]>(`${this.apiUrl}/atribuicoes/`);
  }

  // 2. Criar nova atribuição (Ligar Professor a Turma/Disciplina)
  criar(dados: AtribuicaoCreate): Observable<Atribuicao> {
    return this.http.post<Atribuicao>(`${this.apiUrl}/atribuicoes/`, dados);
  }

  // 3. Remover atribuição
  remover(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/atribuicoes/${id}`);
  }

  // 4. Buscar apenas lista de professores (Helper)
  getProfessores(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/usuarios/professores`);
  }
}
