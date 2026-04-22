import { Routes } from "@angular/router";

export const alunoRoutes: Routes = [
  {
    path: 'novo-aluno',
    loadComponent: () => import('../components/aluno-form/aluno-form').then(m => m.AlunoForm),
  },
  {
    path: 'lista-alunos',
    loadComponent: () => import('../components/aluno-list/aluno-list').then(m => m.AlunoList),
  },
  {
    path: 'aluno/:id/boletim',
    loadComponent: () => import('../components/aluno-boletim/aluno-boletim').then(m => m.AlunoBoletim),
  },
  {
    path: 'aluno/:id/financeiro',
    loadComponent: () => import('../components/aluno-financeiro/aluno-financeiro').then(m => m.AlunoFinanceiro),
  },
  {
    path: 'editar-aluno/:id',
    loadComponent: () => import('../components/aluno-form/aluno-form').then(m => m.AlunoForm),
  },
];
