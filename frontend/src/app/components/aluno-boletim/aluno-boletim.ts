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

  // CORREÇÃO: Inicializa como null, pois é um único objeto, não uma lista array
  boletim = signal<Boletim | null>(null);

  dataHoje = new Date();
  trimestres = ['1º Trimestre', '2º Trimestre', '3º Trimestre'];

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.alunoService.getBoletim(Number(id)).subscribe(dados => {
        // CORREÇÃO: Agora o tipo bate certo (Boletim)
        this.boletim.set(dados);
      });
    }
  }

  // Retorna string formatada para o HTML
  getNota(notas: any[], trimestre: string): string {
    const nota = notas.find(n => n.trimestre === trimestre);
    return nota && nota.valor !== null ? nota.valor.toFixed(1) : '-';
  }

  // Retorna número puro para lógica de cores
  getValorNota(notas: any[], trimestre: string): number | null {
    const nota = notas.find(n => n.trimestre === trimestre);
    return nota ? nota.valor : null;
  }

  calcularMediaGeral(): number {
    const dados = this.boletim(); // CORREÇÃO: Acede ao valor do signal
    if (!dados || !dados.linhas.length) return 0;

    const linhasValidas = dados.linhas.filter(l => l.media_provisoria > 0);

    if (linhasValidas.length === 0) return 0;

    const soma = linhasValidas.reduce((acc, curr) => acc + curr.media_provisoria, 0);
    return soma / linhasValidas.length;
  }

  imprimir() {
    const dados = this.boletim(); // CORREÇÃO: Acede ao valor do signal
    if (dados) {
      const nomeArquivo = `Boletim_${dados.aluno_nome}`;
      this.pdfService.gerarPDF('conteudo-boletim', nomeArquivo);
    }
  }
}
