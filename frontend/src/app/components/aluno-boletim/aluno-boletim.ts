import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AlunoService, Boletim } from '../../services/aluno.service';

@Component({
  selector: 'app-aluno-boletim',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './aluno-boletim.html',
})
export class AlunoBoletim implements OnInit {
  private route = inject(ActivatedRoute);
  private alunoService = inject(AlunoService);
  private cdr = inject(ChangeDetectorRef);

  boletim: Boletim | null = null;
  dataHoje = new Date();

  // Definir trimestres padrão
  trimestres = ['1º Trimestre', '2º Trimestre', '3º Trimestre'];

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.alunoService.getBoletim(Number(id)).subscribe(dados => {
        // Garantir que todas as disciplinas tenham notas para todos os trimestres
        this.boletim = this.estruturarBoletim(dados);
        this.cdr.detectChanges();
      });
    }
  }

  // Estruturar o boletim para garantir dados completos
  estruturarBoletim(boletim: Boletim): Boletim {
    return {
      ...boletim,
      linhas: boletim.linhas.map(linha => {
        // Garantir que cada disciplina tenha entrada para todos os trimestres
        const notasCompletas = this.trimestres.map(trimestre => {
          const notaExistente = linha.notas.find(n => n.trimestre === trimestre);
          return notaExistente || {
            trimestre,
            valor: null,
            descricao: 'Sem nota'
          };
        });

        return {
          ...linha,
          notas: notasCompletas
        };
      })
    };
  }

  getNota(notas: any[], trimestre: string): string {
    const nota = notas.find(n => n.trimestre === trimestre);
    return nota && nota.valor !== null ? nota.valor.toFixed(1) : '-';
  }

  calcularMediaDisciplina(notas: any[]): number {
    const valores = notas
      .filter(n => n.valor !== null)
      .map(n => n.valor);

    if (valores.length === 0) return 0;

    return valores.reduce((a, b) => a + b, 0) / valores.length;
  }

  // ADICIONAR ESTA FUNÇÃO QUE ESTÁ FALTANDO
  calcularMediaGeral(): number {
    if (!this.boletim || !this.boletim.linhas.length) return 0;

    // Filtrar disciplinas que têm média positiva
    const medias = this.boletim.linhas
      .filter(linha => linha.media_provisoria > 0)
      .map(linha => linha.media_provisoria);

    if (medias.length === 0) return 0;

    // Calcular média geral
    return medias.reduce((a, b) => a + b, 0) / medias.length;
  }

  imprimir() {
    window.print();
  }
}
