import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface HorarioSlot {
  id: number;
  dia_semana: number; // 0=Segunda ... 4=Sexta
  hora_inicio: string;
  hora_fim: string;
  disciplina_id?: number;
  professor_id?: number;
  disciplina_nome?: string;
  professor_nome?: string;
}

@Injectable({
  providedIn: 'root'
})
export class HorarioService {
  private http = inject(HttpClient);
  private apiUrl = 'http://127.0.0.1:8000';

  // 6. Rota Rápida: Aulas de Hoje do Professor Logado
  getMeuHorarioHoje(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/meus-horarios-hoje`);
  }

  // 1. Obter Horário da Turma
  getHorarioTurma(turmaId: number): Observable<HorarioSlot[]> {
    return this.http.get<HorarioSlot[]>(`${this.apiUrl}/turmas/${turmaId}/horario`);
  }

  // 2. Gerar Grade Automática (Vazia)
  gerarAutomatico(turmaId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/turmas/${turmaId}/horario/gerar`, {});
  }

  // 3. Atualizar um Slot (Definir Prof/Disciplina)
  atualizarSlot(id: number, dados: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/horarios/${id}`, dados);
  }

  // 4. Validar se Professor pode dar aula AGORA
  validarTempo(horarioId: number): Observable<{pode: boolean, msg: string}> {
    return this.http.get<{pode: boolean, msg: string}>(`${this.apiUrl}/horarios/${horarioId}/validar-tempo`);
  }

  // 5. Fechar o Diário (Finalizar Aula)
  fecharDiario(dados: {horario_id: number, resumo_aula: string}): Observable<any> {
    return this.http.post(`${this.apiUrl}/diarios/fechar`, dados);
  }
}
