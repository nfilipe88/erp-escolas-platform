import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { TurmaService, Turma } from '../../services/turma.service';
import { AlunoService, Aluno } from '../../services/aluno.service'; // <--- Adicionado 'Aluno'
import { PresencaService, PresencaItem } from '../../services/presenca.service';

@Component({
  selector: 'app-turma-chamada',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './turma-chamada.html',
  styleUrl: './turma-chamada.css'
})
export class TurmaChamada implements OnInit {
  private route = inject(ActivatedRoute);
  private turmaService = inject(TurmaService);
  private alunoService = inject(AlunoService);
  private presencaService = inject(PresencaService);
  private cdr = inject(ChangeDetectorRef);

  turma: Turma | null = null;
  listaPresenca: PresencaItem[] = [];

  // Data de Hoje (formato YYYY-MM-DD para o input type="date")
  dataSelecionada = new Date().toISOString().split('T')[0];
  sucesso = '';

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.carregarTurma(Number(id));
    }
  }

  carregarTurma(id: number) {
    // 1. Busca dados da turma
    this.turmaService.getTurmaById(id).subscribe(t => {
      this.turma = t;
      this.carregarAlunos(id);
      this.cdr.detectChanges();
    });
  }

  carregarAlunos(turmaId: number) {
    // 2. Busca alunos DIRETAMENTE da turma (Correção aqui)
    // Usamos o método correto 'getAlunosPorTurma' que definiste no service
    this.alunoService.getAlunosPorTurma(turmaId).subscribe((alunos: Aluno[]) => {

      // Inicializa a lista local
      this.listaPresenca = alunos.map(a => ({
        aluno_id: a.id!,
        aluno_nome: a.nome,
        presente: true,     // Padrão: Veio
        justificado: false,
        observacao: ''
      }));
      // 3. Verifica se já existe chamada nesta data
      this.verificarExistencia();
      this.cdr.detectChanges();
    });
  }

  verificarExistencia() {
    if (!this.turma) return;

    this.presencaService.lerChamada(this.turma.id!, this.dataSelecionada).subscribe(registros => {
      if (registros.length > 0) {
        // Se já existe, atualiza a nossa lista local com o que veio do banco
        registros.forEach(reg => {
          const item = this.listaPresenca.find(i => i.aluno_id === reg.aluno_id);
          if (item) {
            item.presente = reg.presente;
            item.justificado = reg.justificado;
            item.observacao = reg.observacao;
          }
        });
      }
    });
  }

  salvar() {
    if (!this.turma) return;

    const payload = {
      turma_id: this.turma.id!,
      data: this.dataSelecionada,
      lista_alunos: this.listaPresenca
    };

    this.presencaService.salvarChamada(payload).subscribe(() => {
      this.sucesso = 'Chamada registada com sucesso!';
      setTimeout(() => this.sucesso = '', 3000);
    });
  }
}
