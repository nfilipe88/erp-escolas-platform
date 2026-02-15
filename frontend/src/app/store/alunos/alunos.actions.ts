// frontend/src/app/store/alunos/alunos.actions.ts
// import { createAction, props } from '@ngrx/store';
import { Aluno } from '../../services/aluno.service';

// Load Alunos
export const loadAlunos = createAction(
  '[Alunos] Load Alunos',
  props<{ page?: number; filters?: any }>()
);

export const loadAlunosSuccess = createAction(
  '[Alunos] Load Alunos Success',
  props<{ alunos: Aluno[]; pagination: any }>()
);

export const loadAlunosFailure = createAction(
  '[Alunos] Load Alunos Failure',
  props<{ error: string }>()
);

// Create Aluno
export const createAluno = createAction(
  '[Alunos] Create Aluno',
  props<{ aluno: Partial<Aluno> }>()
);

export const createAlunoSuccess = createAction(
  '[Alunos] Create Aluno Success',
  props<{ aluno: Aluno }>()
);

export const createAlunoFailure = createAction(
  '[Alunos] Create Aluno Failure',
  props<{ error: string }>()
);

// Update Aluno
export const updateAluno = createAction(
  '[Alunos] Update Aluno',
  props<{ id: number; aluno: Partial<Aluno> }>()
);

export const updateAlunoSuccess = createAction(
  '[Alunos] Update Aluno Success',
  props<{ aluno: Aluno }>()
);

export const updateAlunoFailure = createAction(
  '[Alunos] Update Aluno Failure',
  props<{ error: string }>()
);

// Delete Aluno
export const deleteAluno = createAction(
  '[Alunos] Delete Aluno',
  props<{ id: number }>()
);

export const deleteAlunoSuccess = createAction(
  '[Alunos] Delete Aluno Success',
  props<{ id: number }>()
);

export const deleteAlunoFailure = createAction(
  '[Alunos] Delete Aluno Failure',
  props<{ error: string }>()
);

// Select Aluno
export const selectAluno = createAction(
  '[Alunos] Select Aluno',
  props<{ aluno: Aluno | null }>()
);

// Set Filters
export const setAlunosFilters = createAction(
  '[Alunos] Set Filters',
  props<{ filters: any }>()
);
