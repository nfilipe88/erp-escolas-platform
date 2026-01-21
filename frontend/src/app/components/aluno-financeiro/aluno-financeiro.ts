import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FinanceiroService, Mensalidade } from '../../services/financeiro.service';
import { AlunoService, Aluno } from '../../services/aluno.service';

@Component({
  selector: 'app-aluno-financeiro',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './aluno-financeiro.html',
  styleUrl: './aluno-financeiro.css'
})
export class AlunoFinanceiro implements OnInit {
  private route = inject(ActivatedRoute);
  private financeiroService = inject(FinanceiroService);
  private alunoService = inject(AlunoService);
  private cdr = inject(ChangeDetectorRef);

  aluno: Aluno | null = null;
  mensalidades: Mensalidade[] = [];
  mensalidadeSelecionada: Mensalidade | null = null; // Para abrir o modal de pagamento

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.carregarDados(Number(id));
    }
  }

  carregarDados(id: number) {
    // Busca dados do aluno (para mostrar o nome)
    this.alunoService.getAlunoById(id).subscribe(a => this.aluno = a);

    // Busca financeiro
    this.financeiroService.getMensalidades(id).subscribe(dados => {
      this.mensalidades = dados;
      this.cdr.detectChanges();
    });
  }

  gerarCarnet() {
    if (this.aluno && confirm('Tem a certeza que quer gerar as mensalidades de 2025?')) {
      this.financeiroService.gerarCarnet(this.aluno.id!, 2025).subscribe(novas => {
        this.mensalidades = novas;
      });
    }
  }

  // Seleciona um mês para pagar
  selecionarParaPagar(m: Mensalidade) {
    if (m.estado === 'Pendente') {
      this.mensalidadeSelecionada = m;
    }
  }

  confirmarPagamento(forma: string) {
    if (this.mensalidadeSelecionada) {
      // 1. Chama o Backend
      this.financeiroService.pagar(this.mensalidadeSelecionada.id, forma).subscribe({
        next: (atualizada) => {

          // 2. Atualiza a lista visualmente (Vermelho -> Verde)
          const index = this.mensalidades.findIndex(m => m.id === atualizada.id);
          if (index !== -1) {
            this.mensalidades[index] = atualizada;
          }

          // 3. --- AQUI ESTÁ A CORREÇÃO ---
          // Forçamos o fecho do modal definindo a variável como null
          this.mensalidadeSelecionada = null;
        },
        error: (err) => {
          alert('Erro ao processar pagamento. Tente novamente.');
        }
      });
    }
  }
}
