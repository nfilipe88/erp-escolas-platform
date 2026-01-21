import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AlunoService, Aluno } from '../../services/aluno.service';
import { TurmaService, Turma, Disciplina } from '../../services/turma.service';
import { CommonModule, DatePipe } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

@Component({
  selector: 'app-turma-detail',
  imports: [CommonModule, RouterLink, ReactiveFormsModule],
  templateUrl: './turma-detail.html',
  styleUrl: './turma-detail.css',
})
export class TurmaDetail implements OnInit {
  private route = inject(ActivatedRoute);
  private turmaService = inject(TurmaService);
  private alunoService = inject(AlunoService);
  private cdr = inject(ChangeDetectorRef);
  private fb = inject(FormBuilder);

  turma: Turma | null = null;
  alunos: Aluno[] = [];
  // Variáveis
  disciplinas: Disciplina[] = [];

  formDisciplina: FormGroup = this.fb.group({
    nome: ['', Validators.required]
  });
  mostrarFormDisciplina = false; // Para esconder/mostrar o formulário

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
      this.cdr.detectChanges();
    });

    // 3. Busca a lista de disciplinas da turma
    this.turmaService.getDisciplinas(id).subscribe(dados => {
      this.disciplinas = dados;
      this.cdr.detectChanges();
    });
  }

  // Função para salvar disciplina
  salvarDisciplina() {
    if (this.formDisciplina.valid && this.turma) {
      const nova: Disciplina = {
        nome: this.formDisciplina.value.nome,
        turma_id: this.turma.id!
      };

      this.turmaService.addDisciplina(nova).subscribe(res => {
        this.disciplinas.push(res); // Adiciona visualmente à lista
        this.formDisciplina.reset();
        this.mostrarFormDisciplina = false;
      });
    }
  }
}
