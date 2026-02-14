import { ChangeDetectorRef, Component, inject, OnInit, signal } from '@angular/core';
import { AlunoService, Aluno } from '../../services/aluno.service';
import { AuthService } from '../../services/auth.service';
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
  private authService = inject(AuthService);
  private route = inject(ActivatedRoute);

  alunos = signal<Aluno[]>([]);
  escolaId: number | null = null;

  ngOnInit() {
    const user = this.authService.getUsuarioLogado();
    if (user && user.escola_id) {
      this.escolaId = user.escola_id;
    } else {
      console.error('Utilizador sem escola associada');
      return;
    }

    this.route.queryParams.subscribe(params => {
      const turmaId = params['turma_id'];
      if (turmaId) {
        this.carregarAlunosDaTurma(Number(turmaId));
      } else {
        this.carregarTodosOsAlunos();
      }
    });
  }

  carregarTodosOsAlunos() {
    if (!this.escolaId) return;
    this.alunoService.getAlunos(this.escolaId).subscribe(dados => {
      this.alunos.set(dados);
    });
  }

  carregarAlunosDaTurma(turmaId: number) {
    this.alunoService.getAlunosPorTurma(turmaId).subscribe(dados => {
      this.alunos.set(dados);
    });
  }

  deletar(id: number) {
    if (confirm("Tens a certeza que queres apagar este aluno?")) {
      this.alunoService.removerAluno(id).subscribe(() => {
        this.ngOnInit(); // recarrega
      });
    }
  }
}
