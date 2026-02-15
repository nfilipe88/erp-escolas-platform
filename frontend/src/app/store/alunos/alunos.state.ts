// frontend/src/app/store/alunos/alunos.state.ts - NOVO ARQUIVO
import { Aluno } from '../../services/aluno.service';

export interface AlunosState {
  alunos: Aluno[];
  selectedAluno: Aluno | null;
  loading: boolean;
  error: string | null;
  filters: {
    search: string;
    turmaId: number | null;
    ativo: boolean | null;
  };
  pagination: {
    page: number;
    perPage: number;
    total: number;
    totalPages: number;
  };
}

export const initialAlunosState: AlunosState = {
  alunos: [],
  selectedAluno: null,
  loading: false,
  error: null,
  filters: {
    search: '',
    turmaId: null,
    ativo: null
  },
  pagination: {
    page: 1,
    perPage: 20,
    total: 0,
    totalPages: 0
  }
};
