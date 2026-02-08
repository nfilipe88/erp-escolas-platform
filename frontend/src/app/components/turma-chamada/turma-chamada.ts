import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AlunoService } from '../../services/aluno.service';
import { PresencaService } from '../../services/presenca.service';

@Component({
  selector: 'app-turma-chamada',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './turma-chamada.html'
})
export class TurmaChamada implements OnInit {
  route = inject(ActivatedRoute);
  router = inject(Router);
  alunoService = inject(AlunoService);
  presencaService = inject(PresencaService);
  private cdr= inject(ChangeDetectorRef);

  turmaId!: number;
  dataSelecionada: string = new Date().toISOString().split('T')[0];
  alunos: any[] = [];
  loading = false;

  ngOnInit() {
    this.turmaId = Number(this.route.snapshot.paramMap.get('id'));
    this.carregarDados();
  }

  carregarDados() {
  this.loading = true;

  // 1. Carregar Alunos da Turma
  this.alunoService.getAlunosPorTurma(this.turmaId).subscribe({
    next: (listaAlunos) => {
      console.log('Alunos carregados:', listaAlunos); // Debug

      if (!listaAlunos || listaAlunos.length === 0) {
        this.alunos = [];
        this.loading = false;
        this.cdr.detectChanges();
        return;
      }

      // 2. Verificar presenças existentes
      this.presencaService.consultar(this.turmaId, this.dataSelecionada).subscribe({
        next: (presencas: any[]) => {
          console.log('Presenças existentes:', presencas); // Debug

          this.alunos = listaAlunos.map(aluno => {
            // Garantir que estamos usando a chave correta
            const registo = presencas?.find((p: any) =>
              p.aluno_id === aluno.id ||
              p.aluno?.id === aluno.id ||
              p.alunoId === aluno.id
            );

            // Status padrão é 'P' (Presente)
            let status = 'P';

            if (registo) {
              // Verificar diferentes possíveis nomes de campo
              status = registo.status || registo.presenca || 'P';
            }

            return {
              ...aluno,
              status: status
            };
          });

          this.cdr.detectChanges();
          this.loading = false;
        },
        error: (error) => {
          console.error('Erro ao carregar presenças:', error);

          // Se erro, todos os alunos como presentes por padrão
          this.alunos = listaAlunos.map(aluno => ({
            ...aluno,
            status: 'P'
          }));

          this.cdr.detectChanges();
          this.loading = false;
        }
      });
    },
    error: (error) => {
      console.error('Erro ao carregar alunos:', error);
      this.alunos = [];
      this.loading = false;
      this.cdr.detectChanges();
    }
  });
}

  mudarStatus(aluno: any) {
    // Ciclo: P (Presente) -> F (Falta) -> FJ (Falta Justificada) -> P
    if (aluno.status === 'P') aluno.status = 'F';
    else if (aluno.status === 'F') aluno.status = 'FJ';
    else aluno.status = 'P';
  }

  salvarChamada() {
    const payload = {
      turma_id: this.turmaId,
      data: this.dataSelecionada,
      lista: this.alunos.map(a => ({
        aluno_id: a.id,
        status: a.status
      }))
    };

    this.presencaService.registar(payload).subscribe({
      next: () => {
        alert('Chamada registada com sucesso! ✅');
        this.router.navigate(['/']); // Volta ao dashboard ou mantém na página
      },
      error: () => alert('Erro ao salvar chamada.')
    });
  }
}
