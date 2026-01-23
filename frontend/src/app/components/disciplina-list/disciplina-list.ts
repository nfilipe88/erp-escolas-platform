import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DisciplinaService, Disciplina } from '../../services/disciplina.service';

@Component({
  selector: 'app-disciplina-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './disciplina-list.html'
})
export class DisciplinaList implements OnInit {
  private service = inject(DisciplinaService);
  private cdr= inject(ChangeDetectorRef);

  disciplinas: Disciplina[] = [];
  // nova: Disciplina = { nome: '', codigo: '', carga_horaria: 80 };

  // Objeto do formulário
  formDisciplina: Disciplina = { nome: '', codigo: '', carga_horaria: 80 };
  // Controlo se estamos a Criar ou Editar
  editandoId: number | null = null;

  ngOnInit() {
    this.carregar();
  }

  carregar() {
    this.service.getDisciplinas().subscribe(d => {
      this.disciplinas = d;
      this.cdr.detectChanges();
    });
  }

  salvar() {
    if (this.editandoId) {
      // MODO EDIÇÃO
      this.service.atualizar(this.editandoId, this.formDisciplina).subscribe(() => {
        this.carregar();
        this.cancelarEdicao(); // Limpa o form
      });
    } else {
      // MODO CRIAÇÃO
      this.service.criar(this.formDisciplina).subscribe(() => {
        this.carregar();
        this.cancelarEdicao(); // Limpa o form
      });
    }
  }

  iniciarEdicao(d: Disciplina) {
    this.editandoId = d.id!;
    // Copia os dados para o formulário
    this.formDisciplina = { nome: d.nome, codigo: d.codigo, carga_horaria: d.carga_horaria };
  }

  cancelarEdicao() {
    this.editandoId = null;
    this.formDisciplina = { nome: '', codigo: '', carga_horaria: 80 };
  }

  eliminar(d: Disciplina) {
    // ALERTA DE SEGURANÇA MÁXIMA
    const mensagem = `⚠️ ATENÇÃO: Tem a certeza que deseja eliminar a disciplina "${d.nome}"?\n\n` +
                     `Isto irá removê-la de TODAS AS TURMAS onde está associada e poderá afetar as pautas e históricos dos alunos.`;

    if (confirm(mensagem)) {
      this.service.eliminar(d.id!).subscribe(() => {
        this.carregar();
      });
    }
  }
}
