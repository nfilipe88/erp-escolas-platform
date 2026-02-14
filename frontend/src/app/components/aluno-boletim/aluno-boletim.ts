import { ChangeDetectorRef, Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AlunoService, Boletim } from '../../services/aluno.service';
import { PdfService } from '../../services/pdf.service';

@Component({
  selector: 'app-aluno-boletim',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './aluno-boletim.html',
})
export class AlunoBoletim implements OnInit {
  private route = inject(ActivatedRoute);
  private alunoService = inject(AlunoService);
  private pdfService = inject(PdfService);

  boletim = signal<Boletim | null>(null);
  dataHoje = new Date();
  trimestres = ['1º Trimestre', '2º Trimestre', '3º Trimestre'];

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.alunoService.getBoletim(Number(id)).subscribe(dados => {
        this.boletim.set(dados);
      });
    }
  }

  getNota(notas: any[], trimestre: string): string {
    const nota = notas.find(n => n.trimestre === trimestre);
    return nota && nota.valor !== null ? nota.valor.toFixed(1) : '-';
  }

  getValorNota(notas: any[], trimestre: string): number | null {
    const nota = notas.find(n => n.trimestre === trimestre);
    return nota ? nota.valor : null;
  }

  calcularMediaGeral(): number {
    const dados = this.boletim();
    if (!dados || !dados.linhas.length) return 0;
    const soma = dados.linhas.reduce((acc, linha) => acc + (linha.media_provisoria || 0), 0);
    return dados.linhas.length ? soma / dados.linhas.length : 0;
  }

  imprimir() {
    const dados = this.boletim();
    if (dados) {
      const nomeArquivo = `Boletim_${dados.aluno_nome}`;
      this.pdfService.gerarPDF('conteudo-boletim', nomeArquivo);
    }
  }
}
