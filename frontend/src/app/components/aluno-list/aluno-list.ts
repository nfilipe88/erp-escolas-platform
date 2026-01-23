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
    // 3. Lê o URL para ver se tem "?turma_id=X"
    this.route.queryParams.subscribe(params => {
      const turmaId = params['turma_id'];

      if (turmaId) {
        this.carregarAlunosDaTurma(Number(turmaId));
      } else {
        this.carregarTodos();
      }
    });
  }

  // carregarAlunos() {
  //   this.alunoService.getAlunos(this.escolaId).subscribe({
  //     next: (dados) => {
  //       this.alunos = dados;
  //       this.cdr.detectChanges(); // <--- Força o Angular a pintar a tela AGORA
  //     },
  //     error: (erro) => {
  //       console.error('Erro ao buscar alunos', erro);
  //     }
  //   });
  // }

  carregarTodos() {
    this.alunoService.getAlunos(0, 100).subscribe(dados => this.alunos = dados);
    this.cdr.detectChanges();
  }

  carregarAlunosDaTurma(turmaId: number) {
    this.alunoService.getAlunosPorTurma(turmaId).subscribe(dados => this.alunos = dados);
    this.cdr.detectChanges();
  }

  deletar(id: number) {
    if (confirm("Tens a certeza que queres apagar este aluno?")) {
      this.alunoService.removerAluno(id).subscribe({
        next: () => {
          // Remove da lista visualmente sem precisar recarregar a página
          this.alunos = this.alunos.filter(a => a.id !== id);
        },
        error: (err) => alert("Erro ao apagar aluno.")
      })
    }
  }
}
