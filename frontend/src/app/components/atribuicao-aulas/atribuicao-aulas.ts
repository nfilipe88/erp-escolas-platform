import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AtribuicaoService, Atribuicao, AtribuicaoCreate } from '../../services/atribuicao.service';
import { TurmaService } from '../../services/turma.service';
import { DisciplinaService } from '../../services/disciplina.service';

@Component({
  selector: 'app-atribuicao-aulas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './atribuicao-aulas.html'
})
export class AtribuicaoAulas implements OnInit {
  private atribuicaoService = inject(AtribuicaoService);
  private turmaService = inject(TurmaService);
  private disciplinaService = inject(DisciplinaService);

  // Listas para os Selects
  turmas: any[] = [];
  disciplinas: any[] = [];
  professores: any[] = [];

  // Lista da Tabela
  atribuicoes: Atribuicao[] = [];

  // Formulário
  novo: AtribuicaoCreate = {
    turma_id: 0,
    disciplina_id: 0,
    professor_id: 0
  };

  ngOnInit() {
    this.carregarListas();
    this.carregarAtribuicoes();
  }

  carregarListas() {
    this.turmaService.getTurmas().subscribe(data => this.turmas = data);
    this.disciplinaService.getDisciplinas().subscribe(data => this.disciplinas = data);
    this.atribuicaoService.getProfessores().subscribe(data => this.professores = data);
  }

  carregarAtribuicoes() {
    this.atribuicaoService.getAtribuicoes().subscribe(data => this.atribuicoes = data);
  }

  salvar() {
    // Validação simples
    if (this.novo.turma_id == 0 || this.novo.disciplina_id == 0 || this.novo.professor_id == 0) {
      alert('Selecione Turma, Disciplina e Professor!');
      return;
    }

    // Converter para número (o HTML às vezes manda string)
    const payload = {
      turma_id: Number(this.novo.turma_id),
      disciplina_id: Number(this.novo.disciplina_id),
      professor_id: Number(this.novo.professor_id)
    };

    this.atribuicaoService.criar(payload).subscribe({
      next: (res) => {
        // Adiciona à lista localmente para não ter de recarregar tudo
        // (Ou podes chamar carregarAtribuicoes() de novo)
        this.carregarAtribuicoes();

        alert('Professor atribuído com sucesso!');
        // Reset simples dos campos
        this.novo.disciplina_id = 0;
      },
      error: (err) => alert('Erro ao atribuir. Verifique se já existe professor para esta disciplina nesta turma.')
    });
  }

  remover(id: number) {
    if(confirm('Tem a certeza que quer remover este professor desta disciplina?')) {
      this.atribuicaoService.remover(id).subscribe(() => {
        this.atribuicoes = this.atribuicoes.filter(a => a.id !== id);
      });
    }
  }
}
