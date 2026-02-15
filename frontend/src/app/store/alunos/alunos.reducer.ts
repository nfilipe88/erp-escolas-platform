// frontend/src/app/store/alunos/alunos.reducer.ts
// import { createReducer, on } from '@ngrx/store';
import { initialAlunosState } from './alunos.state';
import * as AlunosActions from './alunos.actions';

export const alunosReducer = createReducer(
  initialAlunosState,

  // Load Alunos
  on(AlunosActions.loadAlunos, (state) => ({
    ...state,
    loading: true,
    error: null
  })),

  on(AlunosActions.loadAlunosSuccess, (state, { alunos, pagination }) => ({
    ...state,
    alunos,
    pagination,
    loading: false,
    error: null
  })),

  on(AlunosActions.loadAlunosFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),

  // Create Aluno
  on(AlunosActions.createAluno, (state) => ({
    ...state,
    loading: true
  })),

  on(AlunosActions.createAlunoSuccess, (state, { aluno }) => ({
    ...state,
    alunos: [aluno, ...state.alunos],
    loading: false,
    error: null
  })),

  on(AlunosActions.createAlunoFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),

  // Update Aluno
  on(AlunosActions.updateAluno, (state) => ({
    ...state,
    loading: true
  })),

  on(AlunosActions.updateAlunoSuccess, (state, { aluno }) => ({
    ...state,
    alunos: state.alunos.map(a => a.id === aluno.id ? aluno : a),
    selectedAluno: state.selectedAluno?.id === aluno.id ? aluno : state.selectedAluno,
    loading: false,
    error: null
  })),

  on(AlunosActions.updateAlunoFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),

  // Delete Aluno
  on(AlunosActions.deleteAluno, (state) => ({
    ...state,
    loading: true
  })),

  on(AlunosActions.deleteAlunoSuccess, (state, { id }) => ({
    ...state,
    alunos: state.alunos.filter(a => a.id !== id),
    selectedAluno: state.selectedAluno?.id === id ? null : state.selectedAluno,
    loading: false,
    error: null
  })),

  on(AlunosActions.deleteAlunoFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  })),

  // Select Aluno
  on(AlunosActions.selectAluno, (state, { aluno }) => ({
    ...state,
    selectedAluno: aluno
  })),

  // Set Filters
  on(AlunosActions.setAlunosFilters, (state, { filters }) => ({
    ...state,
    filters: { ...state.filters, ...filters }
  }))
);
