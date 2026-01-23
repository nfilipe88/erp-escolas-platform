import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { AlunoService, Aluno } from '../../services/aluno.service';
import { CommonModule, DatePipe } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';

@Component({
  selector: 'app-aluno-list',
  imports: [CommonModule, DatePipe, RouterLink],
  templateUrl: './aluno-list.html',
  styleUrl: './aluno-list.css',
})
export class AlunoList implements OnInit {
  private alunoService = inject(AlunoService);
  private route = inject(ActivatedRoute);
  private cdr = inject(ChangeDetectorRef);

  alunos: Aluno[] = [];
  escolaId = 1; // Fixo para teste

  ngOnInit() {
    // Escuta os parâmetros do URL para ver se existe um filtro de turma
    this.route.queryParams.subscribe(params => {
      const turmaId = params['turma_id'];

      if (turmaId) {
        // Se veio do botão da turma, carrega só os dessa turma
        this.carregarAlunosDaTurma(Number(turmaId));
      } else {
        // Se clicou no menu principal, carrega todos os alunos da escola
        this.carregarTodosOsAlunos();
      }
    });
  }

  carregarTodosOsAlunos() {
    // Passamos o ID da Escola (ex: 1)
    this.alunoService.getAlunos(1).subscribe(dados => {
      this.alunos = dados;
      this.cdr.detectChanges();
    });
  }

  carregarAlunosDaTurma(turmaId: number) {
    this.alunoService.getAlunosPorTurma(turmaId).subscribe(dados => {
      this.alunos = dados;
      this.cdr.detectChanges();
    });
  }

  deletar(id: number) {
    if (confirm("Tens a certeza que queres apagar este aluno?")) {
      this.alunoService.removerAluno(id).subscribe(() => {
        // Após eliminar, recarrega a lista baseada no URL atual
        this.ngOnInit();
      });
    }
  }
}
