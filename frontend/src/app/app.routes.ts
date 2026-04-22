import { Component } from '@angular/core';
import { Routes } from '@angular/router';
import { EscolaForm } from './components/escola-form/escola-form';
import { AlunoForm } from './components/aluno-form/aluno-form';
import { AlunoList } from './components/aluno-list/aluno-list';
import { TurmaForm } from './components/turma-form/turma-form';
import { TurmaList } from './components/turma-list/turma-list';
import { TurmaDetail } from './components/turma-detail/turma-detail';
import { NotaPauta } from './components/nota-pauta/nota-pauta';
import { AlunoBoletim } from './components/aluno-boletim/aluno-boletim';
import { Dashboard } from './components/dashboard/dashboard';
import { AlunoFinanceiro } from './components/aluno-financeiro/aluno-financeiro';
import { AlunoRecibo } from './components/aluno-recibo/aluno-recibo';
import { Login } from './components/login/login';
import { authGuard } from './guards/auth.guard';
import { UsuarioPerfil } from './components/usuario-perfil/usuario-perfil';
import { EsqueciSenha } from './components/esqueci-senha/esqueci-senha';
import { ResetSenha } from './components/reset-senha/reset-senha';
import { TurmaChamada } from './components/turma-chamada/turma-chamada';
import { DisciplinaList } from './components/disciplina-list/disciplina-list';
import { ConfiguracoesPainel } from './components/configuracoes-painel/configuracoes-painel';
import { EscolaDetail } from './components/escola-detail/escola-detail';
import { EscolaList } from './components/escola-list/escola-list';
import { AtribuicaoAulas } from './components/atribuicao-aulas/atribuicao-aulas';
import { UsuarioForm } from './components/usuario-form/usuario-form';
import { UsuarioList } from './components/usuario-list/usuario-list';
import { GestaoHorario } from './components/gestao-horario/gestao-horario';
import { PontoProfessores } from './components/ponto-professores/ponto-professores';
import { RelatoriosFinanceiros } from './components/relatorios-financeiros/relatorios-financeiros';

export const routes: Routes = [
  // Rotas públicas(livres)
  {
    path: 'login',
    loadComponent: () => import('./components/login/login').then(m => m.Login)
  },
  {
    path: 'esqueci-senha',
    loadComponent: () => import('./components/esqueci-senha/esqueci-senha').then(m => m.EsqueciSenha)
  },
  {
    path: 'reset-senha',
    loadComponent: () => import('./components/reset-senha/reset-senha').then(m => m.ResetSenha)
  },
  // Rotas protegidas (precisam de autenticação)
  {
    path: '',
    canActivate: [authGuard],
    children: [
      {
        path: 'dashboard',
        loadComponent: () => import('./components/dashboard/dashboard').then(m => m.Dashboard),
      },
      {
        path: 'nova-escola',
        loadComponent:()=> import('./components/escola-form/escola-form').then(m => m.EscolaForm),
      },
      {
        path: 'escolas',
        loadComponent: () => import('./components/escola-list/escola-list').then(m => m.EscolaList),
      },
      {
        path: 'nova-turma',
        loadComponent: () => import('./components/turma-form/turma-form').then(m => m.TurmaForm),
      },
      {
        path: 'lista-turmas',
        loadComponent: () => import('./components/turma-list/turma-list').then(m => m.TurmaList),
      },
      {
        path: 'turma/:id',
        loadComponent: () => import('./components/turma-detail/turma-detail').then(m => m.TurmaDetail),
      },
      {
        path: 'turma/:turmaId/pauta',
        loadComponent: () => import('./components/nota-pauta/nota-pauta').then(m => m.NotaPauta),
      },
      {
        path: 'recibo/:id',
        loadComponent: () => import('./components/aluno-recibo/aluno-recibo').then(m => m.AlunoRecibo),
      },
      {
        path: 'perfil',
        loadComponent: () => import('./components/usuario-perfil/usuario-perfil').then(m => m.UsuarioPerfil),
      },
      {
        path: 'turma/:turmaId/chamada',
        loadComponent: () => import('./components/turma-chamada/turma-chamada').then(m => m.TurmaChamada),
      },
      {
        path: 'disciplinas',
        loadComponent: () => import('./components/disciplina-list/disciplina-list').then(m => m.DisciplinaList),
      },
      {
        path: 'configuracoes',
        loadComponent: () => import('./components/configuracoes-painel/configuracoes-painel').then(m => m.ConfiguracoesPainel),
      },
      {
        path: 'escolas/:id',
        loadComponent: () => import('./components/escola-detail/escola-detail').then(m => m.EscolaDetail),
      },
      {
        path: 'distribuicao-docente',
        loadComponent: () => import('./components/atribuicao-aulas/atribuicao-aulas').then(m => m.AtribuicaoAulas),
      },
      {
        path: 'pauta/:turmaId/:disciplinaId',
        loadComponent:()=> import('./components/nota-pauta/nota-pauta').then(m => m.NotaPauta)
      },
      {
        path: 'usuarios',
        loadComponent: () => import('./components/usuario-list/usuario-list').then(m => m.UsuarioList)
      },
      {
        path: 'novo-usuario',
        loadComponent: () => import('./components/usuario-form/usuario-form').then(m => m.UsuarioForm)
      },
      {
        path: 'chamada/:id',
        loadComponent: () => import('./components/turma-chamada/turma-chamada').then(m => m.TurmaChamada)
      },
      {
        path: 'gestao-horarios',
        loadComponent: () => import('./components/gestao-horario/gestao-horario').then(m => m.GestaoHorario)
      }, // Rota para gestão de horário
      {
        path: 'ponto-professores',
        loadComponent: () => import('./components/ponto-professores/ponto-professores').then(m => m.PontoProfessores)
      }, // Rota para ponto eletrônico
      {
        path: 'relatorios-financeiros',
        loadComponent: () => import('./components/relatorios-financeiros/relatorios-financeiros').then(m => m.RelatoriosFinanceiros)
      }, // Rota para relatórios financeiros
    ]
  },
  {
    // 2. O Módulo de Alunos (A Mágica do Lazy Loading)
    path: 'alunos',
    // O loadChildren importa o ficheiro 'aluno.routers.ts' de forma assíncrona
    // e extrai a constante 'alunoRoutes' que criámos no Passo 1.
    canActivate:[authGuard], // Adicionamos o Guard à matriz canActivate
    loadChildren: () => import('./routers/aluno.routers').then(m => m.alunoRoutes)
  },
  {
    path: '**',
    redirectTo: 'login'
  } // Rota curinga para redirecionar rotas inválidas
];
