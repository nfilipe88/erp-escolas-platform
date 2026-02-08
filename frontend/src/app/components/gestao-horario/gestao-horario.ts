import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TurmaService } from '../../services/turma.service';
import { HorarioService, HorarioSlot } from '../../services/horario.service';
import { DisciplinaService } from '../../services/disciplina.service';
import { AtribuicaoService } from '../../services/atribuicao.service'; // Para buscar professores

@Component({
  selector: 'app-gestao-horario',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './gestao-horario.html'
})
export class GestaoHorario implements OnInit {
  turmaService = inject(TurmaService);
  horarioService = inject(HorarioService);
  disciplinaService = inject(DisciplinaService);
  atribuicaoService = inject(AtribuicaoService);

  turmas: any[] = [];
  disciplinas: any[] = [];
  professores: any[] = [];

  turmaSelecionada: number = 0;
  grade: HorarioSlot[] = [];
  diasSemana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta'];

  // Modal de Edição
  slotEditando: HorarioSlot | null = null;
  editForm = { disciplina_id: 0, professor_id: 0 };

  ngOnInit() {
    this.carregarListas();
  }

  carregarListas() {
    this.turmaService.getTurmas().subscribe(d => this.turmas = d);
    this.disciplinaService.getDisciplinas().subscribe(d => this.disciplinas = d);
    this.atribuicaoService.getProfessores().subscribe(d => this.professores = d);
  }

  carregarGrade() {
    if (!this.turmaSelecionada) return;

    this.horarioService.getHorarioTurma(this.turmaSelecionada).subscribe(dados => {
      this.grade = dados;
    });
  }

  gerarGrade() {
    if(confirm('Isto irá apagar o horário atual desta turma e criar um novo vazio. Continuar?')) {
      this.horarioService.gerarAutomatico(this.turmaSelecionada).subscribe(() => {
        this.carregarGrade();
      });
    }
  }

  // Funções de Edição
  abrirEdicao(slot: HorarioSlot) {
    this.slotEditando = slot;
    this.editForm = {
      disciplina_id: slot.disciplina_id || 0,
      professor_id: slot.professor_id || 0
    };
  }

  salvarSlot() {
    if (!this.slotEditando) return;

    // Manter dados originais de tempo, só mudar prof/disc
    const payload = {
      ...this.slotEditando,
      disciplina_id: Number(this.editForm.disciplina_id),
      professor_id: Number(this.editForm.professor_id)
    };

    this.horarioService.atualizarSlot(this.slotEditando.id, payload).subscribe(() => {
      this.slotEditando = null; // Fecha modal
      this.carregarGrade();     // Recarrega visual
    });
  }

  // Helper para filtrar slots por dia
  getSlotsPorDia(diaIndex: number) {
    return this.grade.filter(s => s.dia_semana === diaIndex);
  }
}
