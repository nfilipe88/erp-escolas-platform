// --- ADICIONAR ESTES IMPORTS NO TOPO ---
import { createReducer, on } from '@ngrx/store';
import * as AlunosActions from './alunos.actions';
import { Aluno } from '../../services/aluno.service';

// Definir interface do State se não existir (ou importar de alunos.state.ts se tiveres)
export interface AlunosState {
  alunos: Aluno[];
  selectedAluno: Aluno | null;
  loading: boolean;
  error: string | null;
  filters: any;
  pagination: any;
}

export const initialState: AlunosState = {
  alunos: [],
  selectedAluno: null,
  loading: false,
  error: null,
  filters: {},
  pagination: {}
};

export const alunosReducer = createReducer(
  initialState,

  on(AlunosActions.loadAlunos, (state) => ({
    ...state,
    loading: true,
    error: null
  })),

  on(AlunosActions.loadAlunosSuccess, (state, { alunos, pagination }) => ({
    ...state,
    alunos,
    pagination,
    loading: false
  })),

  on(AlunosActions.loadAlunosFailure, (state, { error }) => ({
    ...state,
    error,
    loading: false
  })),

  on(AlunosActions.createAluno, (state) => ({
    ...state,
    loading: true
  })),

  on(AlunosActions.createAlunoSuccess, (state, { aluno }) => ({
    ...state,
    alunos: [...state.alunos, aluno],
    loading: false
  })),

  on(AlunosActions.createAlunoFailure, (state, { error }) => ({
    ...state,
    error,
    loading: false
  })),

  on(AlunosActions.updateAluno, (state) => ({
    ...state,
    loading: true
  })),

  on(AlunosActions.updateAlunoSuccess, (state, { aluno }) => ({
    ...state,
    alunos: state.alunos.map(a => a.id === aluno.id ? aluno : a),
    loading: false
  })),

  on(AlunosActions.updateAlunoFailure, (state, { error }) => ({
    ...state,
    error,
    loading: false
  })),

  on(AlunosActions.deleteAluno, (state) => ({
    ...state,
    loading: true
  })),

  on(AlunosActions.deleteAlunoSuccess, (state, { id }) => ({
    ...state,
    alunos: state.alunos.filter(a => a.id !== id),
    loading: false
  })),

  on(AlunosActions.deleteAlunoFailure, (state, { error }) => ({
    ...state,
    error,
    loading: false
  })),

  on(AlunosActions.selectAluno, (state, { aluno }) => ({
    ...state,
    selectedAluno: aluno
  })),

  on(AlunosActions.setAlunosFilters, (state, { filters }) => ({
    ...state,
    filters
  }))
);
