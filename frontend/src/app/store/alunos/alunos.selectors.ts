// frontend/src/app/store/alunos/alunos.selectors.ts
import { createFeatureSelector, createSelector } from '@ngrx/store';
import { AlunosState } from './alunos.state';

export const selectAlunosState = createFeatureSelector<AlunosState>('alunos');

export const selectAllAlunos = createSelector(
  selectAlunosState,
  (state) => state.alunos
);

export const selectSelectedAluno = createSelector(
  selectAlunosState,
  (state) => state.selectedAluno
);

export const selectAlunosLoading = createSelector(
  selectAlunosState,
  (state) => state.loading
);

export const selectAlunosError = createSelector(
  selectAlunosState,
  (state) => state.error
);

export const selectAlunosFilters = createSelector(
  selectAlunosState,
  (state) => state.filters
);

export const selectAlunosPagination = createSelector(
  selectAlunosState,
  (state) => state.pagination
);

// Seletor filtrado
export const selectFilteredAlunos = createSelector(
  selectAllAlunos,
  selectAlunosFilters,
  (alunos, filters) => {
    return alunos.filter(aluno => {
      if (filters.search && !aluno.nome.toLowerCase().includes(filters.search.toLowerCase())) {
        return false;
      }
      if (filters.turmaId && aluno.turma_id !== filters.turmaId) {
        return false;
      }
      if (filters.ativo !== null && aluno.ativo !== filters.ativo) {
        return false;
      }
      return true;
    });
  }
);
