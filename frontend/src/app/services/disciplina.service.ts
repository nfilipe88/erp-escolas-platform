import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface Disciplina {
  id?: number;
  nome: string;
  codigo: string;
  carga_horaria: number;
}

@Injectable({ providedIn: 'root' })
export class DisciplinaService {
  private http = inject(HttpClient);
  private apiUrl = 'http://127.0.0.1:8000';

  getDisciplinas(): Observable<Disciplina[]> {
    return this.http.get<Disciplina[]>(`${this.apiUrl}/disciplinas/`);
  }

  criar(dados: Disciplina): Observable<Disciplina> {
    return this.http.post<Disciplina>(`${this.apiUrl}/disciplinas/`, dados);
  }
}
