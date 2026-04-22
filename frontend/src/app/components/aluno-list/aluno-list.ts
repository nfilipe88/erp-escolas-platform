import { ChangeDetectionStrategy, ChangeDetectorRef, Component, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { AlunoService, Aluno } from '../../services/aluno.service';
import { AsyncPipe, CommonModule, DatePipe } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Store } from '@ngrx/store';
import * as AlunosActions from '../../store/alunos/alunos.actions';
import * as fromAlunos from '../../store/alunos/alunos.selectors';
import { Observable, Subscription } from 'rxjs';

@Component({
  selector: 'app-aluno-list',
  imports: [CommonModule, DatePipe, RouterLink, AsyncPipe],
  templateUrl: './aluno-list.html',
  styleUrl: './aluno-list.css',
  changeDetection: ChangeDetectionStrategy.OnPush  // Importante para performance
})
export class AlunoList implements OnInit, OnDestroy {
  alunos = signal<Aluno[]>([]);
  alunos$: Observable<Aluno[]>;
  loading$: Observable<boolean>;
  error$: Observable<string | null>;
  pagination$: Observable<any>;
  escolaId: number | null = null;
  private subscription: Subscription | null = null;

  constructor(private store: Store) {
    this.alunos$ = this.store.select(fromAlunos.selectAllAlunos);
    this.loading$ = this.store.select(fromAlunos.selectAlunosLoading);
    this.error$ = this.store.select(fromAlunos.selectAlunosError);
    this.pagination$ = this.store.select(fromAlunos.selectAlunosPagination);
  }

  ngOnInit() {
    this.subscription = this.alunos$.subscribe(data => this.alunos.set(data || []));
    this.store.dispatch(AlunosActions.loadAlunos({ page: 1 }));
  }

  ngOnDestroy() {
    this.subscription?.unsubscribe();
  }

  onPageChange(page: number) {
    this.store.dispatch(AlunosActions.loadAlunos({ page }));
  }

  onSearch(search: string) {
    this.store.dispatch(AlunosActions.setAlunosFilters({ filters: { search } }));
    this.store.dispatch(AlunosActions.loadAlunos({ page: 1 }));
  }

  onDeleteAluno(id: number) {
    if (confirm('Tem certeza que deseja deletar este aluno?')) {
      this.store.dispatch(AlunosActions.deleteAluno({ id }));
    }
  }
}
