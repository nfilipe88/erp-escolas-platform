import { NotaPauta } from './../components/nota-pauta/nota-pauta';
import { AtribuicaoAulas } from './../components/atribuicao-aulas/atribuicao-aulas';
import { UsuarioForm } from './../components/usuario-form/usuario-form';
import { Router, Routes } from "@angular/router";

export const professorRoutes: Routes = [
  {
    path: 'novo-professor',
    loadComponent: () => import('../components/usuario-form/usuario-form').then(m => m.UsuarioForm),
  },
  {
    path: 'minhas-turmas',
    loadComponent: () => import('../components/atribuicao-aulas/atribuicao-aulas').then(m => m.AtribuicaoAulas),
  },
  {
    path:'lancar-notas',
    loadComponent: () => import('../components/nota-pauta/nota-pauta').then(m => m.NotaPauta)
  }
];

