import { Routes } from '@angular/router';
import { EscolaForm } from './components/escola-form/escola-form';
import { AlunoForm } from './components/aluno-form/aluno-form';
import { AlunoList } from './components/aluno-list/aluno-list';
import { TurmaForm } from './components/turma-form/turma-form';
import { TurmaList } from './components/turma-list/turma-list';
import { TurmaDetail } from './components/turma-detail/turma-detail';

export const routes: Routes = [
  { path: '', redirectTo: 'nova-escola', pathMatch: 'full' }, // Redireciona a raiz
  { path: 'nova-escola', component: EscolaForm },
  { path: 'novo-aluno', component: AlunoForm },
  { path: 'lista-alunos', component: AlunoList },
  { path: 'editar-aluno/:id', component: AlunoForm },
  { path: 'nova-turma', component: TurmaForm },
  { path: 'lista-turmas', component: TurmaList },
  { path: 'nova-turma', component: TurmaForm },
  { path: 'turma/:id', component: TurmaDetail },
];
