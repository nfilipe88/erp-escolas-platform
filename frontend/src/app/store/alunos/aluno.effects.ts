import { Injectable, inject } from '@angular/core'; // Adicionado 'inject'
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { of } from 'rxjs';
import { map, catchError, switchMap, withLatestFrom } from 'rxjs/operators';
import * as AlunosActions from './alunos.actions';
import * as fromAlunos from './alunos.selectors';
import { AlunoService } from '../../services/aluno.service';

@Injectable()
export class AlunosEffects {

  // 1. Usar inject() do Angular para evitar problemas de sincronização
  private actions$ = inject(Actions);
  private store = inject(Store);
  private alunosService = inject(AlunoService);

  loadAlunos$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AlunosActions.loadAlunos),
      withLatestFrom(this.store.select(fromAlunos.selectAlunosFilters)),
      switchMap(([action, filters]) => {
        // Se a ação não enviar página, assumimos a 1
        const page = action.page || 1;
        // O limite padrão por página
        const limit = 10;

        const mergedFilters = { ...filters, ...action.filters };

        // Agora passamos a página, o limite e os filtros corretamente
        return this.alunosService.getAlunos(page, limit, mergedFilters).pipe(
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

  // 2. O construtor é apagado por completo.
}
