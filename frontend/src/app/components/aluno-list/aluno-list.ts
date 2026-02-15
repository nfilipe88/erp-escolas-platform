import { ChangeDetectionStrategy, ChangeDetectorRef, Component, inject, OnInit, signal } from '@angular/core';
import { AlunoService, Aluno } from '../../services/aluno.service';
import { AuthService } from '../../services/auth.service';
import { CommonModule, DatePipe } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Store } from '@ngrx/store';
import * as AlunosActions from '../../store/alunos/alunos.actions';
import * as fromAlunos from '../../store/alunos/alunos.selectors';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-aluno-list',
  imports: [CommonModule, DatePipe, RouterLink],
  templateUrl: './aluno-list.html',
  styleUrl: './aluno-list.css',
  changeDetection: ChangeDetectionStrategy.OnPush  // Importante para performance
})
export class AlunoList implements OnInit {
  private alunoService = inject(AlunoService);
  private authService = inject(AuthService);
  private route = inject(ActivatedRoute);

  alunos = signal<Aluno[]>([]);
  alunos$: Observable<Aluno[]>;
  loading$: Observable<boolean>;
  error$: Observable<string | null>;
  pagination$: Observable<any>;
  escolaId: number | null = null;

  constructor(private store: Store) {
    this.alunos$ = this.store.select(fromAlunos.selectAllAlunos);
    this.loading$ = this.store.select(fromAlunos.selectAlunosLoading);
    this.error$ = this.store.select(fromAlunos.selectAlunosError);
    this.pagination$ = this.store.select(fromAlunos.selectAlunosPagination);
  }

  ngOnInit() {
    // Carregar alunos
    this.store.dispatch(AlunosActions.loadAlunos({ page: 1 }));
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
