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
    this.alunoService.getAlunosPorTurma(this.turmaId).subscribe(listaAlunos => {

      // 2. Verificar se já houve chamada neste dia
      this.presencaService.consultar(this.turmaId, this.dataSelecionada).subscribe(presencas => {

        // Combinar dados: Se já existe presença, usa o status. Se não, padrão é 'P' (Presente)
        this.alunos = listaAlunos.map(aluno => {
          const registo = presencas.find((p: any) => p.aluno_id === aluno.id);
          return {
            ...aluno,
            status: registo ? registo.status : 'P' // Padrão: Todos Presentes
          };
        });
        this.cdr.detectChanges();

        this.loading = false;
      });
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
