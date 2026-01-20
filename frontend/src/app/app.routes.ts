import { Routes } from '@angular/router';
import { EscolaForm } from './components/escola-form/escola-form';
import { AlunoForm } from './components/aluno-form/aluno-form';
import { AlunoList } from './components/aluno-list/aluno-list';

export const routes: Routes = [
  { path: '', redirectTo: 'nova-escola', pathMatch: 'full' }, // Redireciona a raiz
  { path: 'nova-escola', component: EscolaForm },
  { path: 'novo-aluno', component: AlunoForm },
  { path: 'lista-alunos', component: AlunoList },
  { path: 'editar-aluno/:id', component: AlunoForm },
];
