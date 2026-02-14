import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment.development';

export interface HorarioSlot {
  id: number;
  dia_semana: number;
  hora_inicio: string;
  hora_fim: string;
  disciplina_id?: number;
  professor_id?: number;
  disciplina_nome?: string;
  professor_nome?: string;
}

@Injectable({ providedIn: 'root' })
export class HorarioService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  // ✅ CORRIGIDO (prefixo /horarios)
  getMeuHorarioHoje(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/horarios/meus-horarios-hoje`);
  }

  // ✅ CORRETO
  getHorarioTurma(turmaId: number): Observable<HorarioSlot[]> {
    return this.http.get<HorarioSlot[]>(`${this.apiUrl}/turmas/${turmaId}/horario`);
  }

  // ✅ CORRETO
  gerarAutomatico(turmaId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/turmas/${turmaId}/horario/gerar`, {});
  }

  // ✅ CORRETO
  atualizarSlot(id: number, dados: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/horarios/${id}`, dados);
  }

  // ✅ CORRETO
  validarTempo(horarioId: number): Observable<{ pode: boolean; msg: string }> {
    return this.http.get<{ pode: boolean; msg: string }>(
      `${this.apiUrl}/horarios/${horarioId}/validar-tempo`
    );
  }

  // ✅ CORRIGIDO (endpoint real no backend)
  fecharDiario(dados: { horario_id: number; resumo_aula: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/presencas/diario`, dados);
  }
}
