import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment.development';

export interface Disciplina {
  id?: number;
  nome: string;
  codigo: string;
  carga_horaria: number;
  escola_id?: number;   // ← ADICIONADO (opcional, só para superadmin)
}

@Injectable({ providedIn: 'root' })
export class DisciplinaService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  getDisciplinas(): Observable<Disciplina[]> {
    return this.http.get<Disciplina[]>(`${this.apiUrl}/disciplinas/`);
  }

  criar(dados: Disciplina): Observable<Disciplina> {
    return this.http.post<Disciplina>(`${this.apiUrl}/disciplinas/`, dados);
  }

  atualizar(id: number, dados: Disciplina): Observable<Disciplina> {
    return this.http.put<Disciplina>(`${this.apiUrl}/disciplinas/${id}`, dados);
  }

  eliminar(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/disciplinas/${id}`);
  }
}
