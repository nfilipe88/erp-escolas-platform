import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FinanceiroService } from '../../services/financeiro.service';

@Component({
  selector: 'app-relatorios-financeiros',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './relatorios-financeiros.html'
})
export class RelatoriosFinanceiros implements OnInit {
  financeiroService = inject(FinanceiroService);

  resumo: any = null;
  fluxo: any[] = [];
  devedores: any[] = [];

  abaAtiva: 'fluxo' | 'devedores' = 'fluxo'; // Controle de Tabs

  ngOnInit() {
    this.carregarDados();
  }

  carregarDados() {
    // 1. Carregar Resumo (Cards)
    this.financeiroService.getResumoFinanceiro().subscribe(data => this.resumo = data);

    // 2. Carregar Tabelas
    this.financeiroService.getFluxoCaixa().subscribe(data => this.fluxo = data);
    this.financeiroService.getDevedores().subscribe(data => this.devedores = data);
  }
}
