import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AlunoService, Aluno } from '../../services/aluno.service';
import { TurmaService, Turma } from '../../services/turma.service';
import { CommonModule, DatePipe } from '@angular/common';

@Component({
  selector: 'app-turma-detail',
  imports: [CommonModule, RouterLink],
  templateUrl: './turma-detail.html',
  styleUrl: './turma-detail.css',
})
export class TurmaDetail implements OnInit {
  private route = inject(ActivatedRoute);
  private turmaService = inject(TurmaService);
  private alunoService = inject(AlunoService);
  private cdr = inject(ChangeDetectorRef);

  turma: Turma | null = null;
  alunos: Aluno[] = [];

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.carregarDados(Number(id));
    }
  }

  carregarDados(id: number) {
    // 1. Busca os detalhes da Turma (Nome, Turno, etc.)
    this.turmaService.getTurmaById(id).subscribe(dados => {
      this.turma = dados;
      this.cdr.detectChanges();
    });

    // 2. Busca a lista de chamadas (Alunos desta turma)
    this.alunoService.getAlunosPorTurma(id).subscribe(dados => {
      this.alunos = dados;
    });
  }
}
