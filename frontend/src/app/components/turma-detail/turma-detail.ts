import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AlunoService, Aluno } from '../../services/aluno.service';
import { TurmaService, Turma } from '../../services/turma.service';
import { CommonModule, DatePipe } from '@angular/common';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Disciplina, DisciplinaService } from '../../services/disciplina.service';

@Component({
  selector: 'app-turma-detail',
  imports: [CommonModule, RouterLink, ReactiveFormsModule, FormsModule],
  templateUrl: './turma-detail.html',
  styleUrl: './turma-detail.css',
})
export class TurmaDetail implements OnInit {
  private route = inject(ActivatedRoute);
  private turmaService = inject(TurmaService);
  private alunoService = inject(AlunoService);
  private disciplinaService = inject(DisciplinaService);
  private cdr = inject(ChangeDetectorRef);
  private fb = inject(FormBuilder);

  turma: Turma | null = null;
  alunos: Aluno[] = [];
  // Variáveis
  disciplinasDaTurma: Disciplina[] = [];
  todasDisciplinas: Disciplina[] = []; // O Catálogo Global

  // Controlo do Formulário
  mostrarFormDisciplina = false;
  disciplinaSelecionadaId: number | null = null;

  formDisciplina: FormGroup = this.fb.group({
    nome: ['', Validators.required],
    codigo: ['', Validators.required],
    cargaHoraria: ['', Validators.required],
  });

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.carregarTurma(Number(id));
      this.carregarCatalogoDisciplinas();
    }
  }

  carregarTurma(id: number) {
    // 1. Busca os dados da Turma (agora já traz as disciplinas automaticamente do backend)
    this.turmaService.getTurmaById(id).subscribe(dados => {
      this.turma = dados;
      this.disciplinasDaTurma = dados.disciplinas || [];
      this.cdr.detectChanges();
    });

    // 2. Busca a lista de alunos
    this.alunoService.getAlunosPorTurma(id).subscribe(dados => {
      this.alunos = dados;
      this.cdr.detectChanges();
    });

    // 2. Busca a lista de chamadas (Alunos desta turma)
    this.alunoService.getAlunosPorTurma(id).subscribe(dados => {
      this.alunos = dados;
      this.cdr.detectChanges();
    });

    // 3. Busca a lista de disciplinas da turma
    this.turmaService.getDisciplinasByTurma(id).subscribe(dados => {
      this.disciplinasDaTurma = dados;
      this.cdr.detectChanges();
    });
  }

  // Carrega todas as disciplinas que existem na escola para o Dropdown
  carregarCatalogoDisciplinas() {
    this.disciplinaService.getDisciplinas().subscribe(d => {
      this.todasDisciplinas = d;
      this.cdr.detectChanges();
    });
  }

  // Função para salvar disciplina
  associarDisciplina() {
    if (!this.turma?.id || !this.disciplinaSelecionadaId) return;

    this.turmaService.associarDisciplina(this.turma.id, this.disciplinaSelecionadaId).subscribe({
      next: () => {
        // Sucesso: Recarrega a turma para atualizar a lista visualmente
        this.carregarTurma(this.turma!.id!);
        this.mostrarFormDisciplina = false;
        this.disciplinaSelecionadaId = null; // Limpa o select
      },
      error: (err) => alert('Esta disciplina já está associada à turma!')
    });
  }
}
