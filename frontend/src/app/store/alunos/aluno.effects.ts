// frontend/src/app/store/alunos/alunos.effects.ts
import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { of } from 'rxjs';
import { map, catchError, switchMap, withLatestFrom } from 'rxjs/operators';
import { AlunosService } from '../../services/alunos.service';
import * as AlunosActions from './alunos.actions';
import * as fromAlunos from './alunos.selectors';

@Injectable()
export class AlunosEffects {

  loadAlunos$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AlunosActions.loadAlunos),
      withLatestFrom(this.store.select(fromAlunos.selectAlunosFilters)),
      switchMap(([action, filters]) => {
        const page = action.page || 1;
        const mergedFilters = { ...filters, ...action.filters };

        return this.alunosService.getAlunos(page, mergedFilters).pipe(
          map(response => AlunosActions.loadAlunosSuccess({
            alunos: response.items,
            pagination: {
              page: response.page,
              perPage: response.per_page,
              total: response.total,
              totalPages: response.total_pages
            }
          })),
          catchError(error => of(AlunosActions.loadAlunosFailure({
            error: error.message || 'Erro ao carregar alunos'
          })))
        );
      })
    )
  );

  createAluno$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AlunosActions.createAluno),
      switchMap(action =>
        this.alunosService.createAluno(action.aluno).pipe(
          map(aluno => AlunosActions.createAlunoSuccess({ aluno })),
          catchError(error => of(AlunosActions.createAlunoFailure({
            error: error.message || 'Erro ao criar aluno'
          })))
        )
      )
    )
  );

  updateAluno$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AlunosActions.updateAluno),
      switchMap(action =>
        this.alunosService.updateAluno(action.id, action.aluno).pipe(
          map(aluno => AlunosActions.updateAlunoSuccess({ aluno })),
          catchError(error => of(AlunosActions.updateAlunoFailure({
            error: error.message || 'Erro ao atualizar aluno'
          })))
        )
      )
    )
  );

  deleteAluno$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AlunosActions.deleteAluno),
      switchMap(action =>
        this.alunosService.deleteAluno(action.id).pipe(
          map(() => AlunosActions.deleteAlunoSuccess({ id: action.id })),
          catchError(error => of(AlunosActions.deleteAlunoFailure({
            error: error.message || 'Erro ao deletar aluno'
          })))
        )
      )
    )
  );

  constructor(
    private actions$: Actions,
    private store: Store,
    private alunosService: AlunosService
  ) {}
}
