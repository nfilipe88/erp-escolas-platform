import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

// Definimos o tipo de dados que esperamos (igual ao Schema do Python)
export interface Escola {
  id?: number;
  nome: string;
  slug: string;
  endereco?: string;
}

@Injectable({
  providedIn: 'root',
})
export class EscolaService {
  private http = inject(HttpClient);
  private apiUrl = 'http://127.0.0.1:8000'; // O endereço do teu Python

  constructor() { }

  // Função para enviar os dados para o Backend
  criarEscola(escola: Escola): Observable<Escola> {
    return this.http.post<Escola>(`${this.apiUrl}/escolas/`, escola);
  }
}
