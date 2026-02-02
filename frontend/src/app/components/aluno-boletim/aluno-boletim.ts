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
  trimestres = ['1º Trimestre', '2º Trimestre', '3º Trimestre'];

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.alunoService.getBoletim(Number(id)).subscribe(dados => {
        this.boletim = this.estruturarBoletim(dados);
        this.cdr.detectChanges();
      });
    }
  }

  estruturarBoletim(boletim: Boletim): Boletim {
    return {
      ...boletim,
      linhas: boletim.linhas.map(linha => {
        const notasCompletas = this.trimestres.map(trimestre => {
          const notaExistente = linha.notas.find(n => n.trimestre === trimestre);
          return notaExistente || {
            trimestre,
            valor: null,
            descricao: 'Sem nota'
          };
        });
        return { ...linha, notas: notasCompletas };
      })
    };
  }

  // Retorna string formatada para o HTML
  getNota(notas: any[], trimestre: string): string {
    const nota = notas.find(n => n.trimestre === trimestre);
    return nota && nota.valor !== null ? nota.valor.toFixed(1) : '-';
  }

  // Retorna número puro para lógica de cores (novo helper)
  getValorNota(notas: any[], trimestre: string): number | null {
    const nota = notas.find(n => n.trimestre === trimestre);
    return nota ? nota.valor : null;
  }

  calcularMediaGeral(): number {
    if (!this.boletim || !this.boletim.linhas.length) return 0;

    // Consideramos apenas disciplinas com média > 0 para o cálculo da geral
    const linhasValidas = this.boletim.linhas.filter(l => l.media_provisoria > 0);

    if (linhasValidas.length === 0) return 0;

    const soma = linhasValidas.reduce((acc, curr) => acc + curr.media_provisoria, 0);
    return soma / linhasValidas.length;
  }

  imprimir() {
    window.print();
  }
}
