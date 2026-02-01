import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FinanceiroService, Mensalidade } from '../../services/financeiro.service';
import { AlunoService, Aluno } from '../../services/aluno.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-aluno-financeiro',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './aluno-financeiro.html',
  styleUrl: './aluno-financeiro.css'
})
export class AlunoFinanceiro implements OnInit {
  private route = inject(ActivatedRoute);
  private financeiroService = inject(FinanceiroService);
  private alunoService = inject(AlunoService);
  private cdr = inject(ChangeDetectorRef);

  // aluno: Aluno | null = null;
  // mensalidades: Mensalidade[] = [];
  mensalidadeSelecionada: Mensalidade | null = null; // Para abrir o modal de pagamento
  alunoId!: number;
  aluno: any = null;
  mensalidades: any[] = [];
  anoSelecionado = 2025;

  ngOnInit() {
    this.alunoId = Number(this.route.snapshot.paramMap.get('id'));

    // Carregar nome do aluno
    this.alunoService.getAlunoById(this.alunoId).subscribe(data => this.aluno = data);

    // Carregar financeiro inicial
    this.carregarFinanceiro(); // <--- Agora chamamos o método que vamos criar abaixo
  }

  carregarFinanceiro() {
    this.financeiroService.getMensalidades(this.alunoId).subscribe(data => {
      this.mensalidades = data;
    });
  }

  carregarDados(id: number) {
    this.alunoService.getAlunoById(id).subscribe(a => this.aluno = a);

    this.financeiroService.getMensalidades(id).subscribe(dados => {
      // MAGIA: Antes de mostrar, verifica se há mensalidades atrasadas
      const hoje = new Date();
      this.mensalidades = dados.map(m => {
        const dataVencimento = new Date(m.data_vencimento);
        // Se está pendente e o dia de hoje é maior que o dia de vencimento, muda para "Atrasado"
        if (m.estado === 'Pendente' && hoje > dataVencimento) {
          m.estado = 'Atrasado';
        }
        return m;
      });
      this.cdr.detectChanges();
    });
  }

  gerarCarnet() {
    if(confirm(`Gerar carnet para o ano letivo ${this.anoSelecionado}?`)) {
      this.financeiroService.gerarCarnet(this.alunoId, this.anoSelecionado).subscribe({
        next: (res) => {
          alert('Carnet gerado com sucesso!');
          this.carregarFinanceiro(); // Atualiza a lista
        },
        error: (err) => alert('Erro ao gerar carnet.')
      });
    }
  }

  // Seleciona um mês para pagar
  selecionarParaPagar(m: Mensalidade) {
    if (m.estado === 'Pendente') {
      this.mensalidadeSelecionada = m;
    }
  }

  confirmarPagamento(mensalidade: any) {
    const metodo = prompt('Forma de Pagamento (TPA, Dinheiro, Transferencia):', 'TPA');

    if (metodo) {
      const payload = {
        forma_pagamento: metodo,
        data_pagamento: new Date().toISOString().split('T')[0] // Data de hoje
      };

      // O erro TS2345 desaparece porque o serviço agora aceita objeto
      this.financeiroService.pagar(mensalidade.id, payload).subscribe({
        next: (res) => {
          alert('Pagamento registado com sucesso! 💰');
          this.carregarFinanceiro(); // O erro TS2339 desaparece porque o método existe
        },
        error: (err) => {
          console.error(err);
          alert('Erro ao processar pagamento.');
        }
      });
    }
  }
}
