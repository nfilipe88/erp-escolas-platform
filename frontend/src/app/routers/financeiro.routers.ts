// src/app/routes/financeiro.routes.ts
import { Routes } from '@angular/router';

export const financeiroRoutes: Routes = [
  // O caminho vazio '' representa a raiz deste módulo (ex: se o pai for /financeiro, isto carrega em /financeiro)
  {
    path: '',
    loadComponent: () => import('../components/relatorios-financeiros/relatorios-financeiros').then(c => c.RelatoriosFinanceiros),
    title: 'Dashboard Financeiro' // Dica: podes adicionar o título da página na tab do browser!
  },

  // Caminho: /financeiro/mensalidades
  {
    path: 'mensalidades',
    loadComponent: () => import('../components/aluno-financeiro/aluno-financeiro').then(c => c.AlunoFinanceiro),
    title: 'Gestão de Mensalidades'
  },

  // Caminho: /financeiro/recibos/123 (passando um ID dinâmico)
  {
    path: 'recibos/:id',
    loadComponent: () => import('../components/aluno-recibo/aluno-recibo').then(c => c.AlunoRecibo),
    title: 'Recibo do Aluno'
  },
];
