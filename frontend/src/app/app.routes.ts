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
import { authGuard } from './guards/auth.guard-guard';
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
  { path: 'login', component: Login },
  { path: 'esqueci-senha', component: EsqueciSenha },
  { path: 'reset-senha', component: ResetSenha },
  // Rotas protegidas (precisam de autenticação)
  {
    path: '',
    canActivate: [authGuard],
    children: [
      { path: 'dashboard', component: Dashboard, },
      { path: 'nova-escola', component: EscolaForm, },
      { path: 'novo-aluno', component: AlunoForm, },
      { path: 'lista-alunos', component: AlunoList, },
      { path: 'editar-aluno/:id', component: AlunoForm, },
      { path: 'nova-turma', component: TurmaForm, },
      { path: 'lista-turmas', component: TurmaList, },
      { path: 'nova-turma', component: TurmaForm, },
      { path: 'turma/:id', component: TurmaDetail, },
      { path: 'turma/:turmaId/pauta', component: NotaPauta, },
      { path: 'aluno/:id/boletim', component: AlunoBoletim, },
      { path: 'aluno/:id/financeiro', component: AlunoFinanceiro, },
      { path: 'recibo/:id', component: AlunoRecibo, },
      { path: 'perfil', component: UsuarioPerfil, },
      { path: 'turma/:turmaId/chamada', component: TurmaChamada, },
      { path: 'disciplinas', component: DisciplinaList, },
      { path: 'configuracoes', component: ConfiguracoesPainel, },
      { path: 'escolas', component: EscolaList },
      { path: 'escolas/:id', component: EscolaDetail },
      { path: 'distribuicao-docente', component: AtribuicaoAulas },
      { path: 'pauta/:turmaId/:disciplinaId', component: NotaPauta },
      { path: 'usuarios', component: UsuarioList },
      { path: 'novo-usuario', component: UsuarioForm },
      { path: 'chamada/:id',component: TurmaChamada },
      { path: 'gestao-horarios', component: GestaoHorario }, // Rota para gestão de horário
      { path: 'ponto-professores', component: PontoProfessores }, // Rota para ponto eletrônico
      { path: 'relatorios-financeiros', component: RelatoriosFinanceiros },
    ]
  },
  { path: '**', redirectTo: 'login' } // Rota curinga para redirecionar rotas inválidas
];
