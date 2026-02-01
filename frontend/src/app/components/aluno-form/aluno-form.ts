import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { AlunoService } from '../../services/aluno.service';
import { TurmaService, Turma } from '../../services/turma.service';
import { EscolaService } from '../../services/escola.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-aluno-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './aluno-form.html',
  styleUrl: './aluno-form.css',
})
export class AlunoForm implements OnInit {
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private fb = inject(FormBuilder);
  private alunoService = inject(AlunoService);
  private turmaService = inject(TurmaService);
  private escolaService = inject(EscolaService);
  private authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);

  isEditMode = false;
  isSuperAdmin = false;
  alunoId: number | null = null;
  minhaEscolaId: number | null = null;

  turmas: Turma[] = [];
  escolas: any[] = [];

  mensagemSucesso = '';
  mensagemErro = '';

  form: FormGroup = this.fb.group({
    nome: ['', [Validators.required, Validators.minLength(3)]],
    bi: ['', [Validators.required]],
    data_nascimento: ['', Validators.required],
    escola_id: [null],
    turma_id: [null]
  });

  ngOnInit() {
    // 1. Obter usuário logado
    const user = this.authService.getUsuarioLogado();
    this.isSuperAdmin = user?.perfil === 'superadmin';

    // CORREÇÃO: Tratar explicitamente o tipo
    if (user && user.escola_id !== undefined) {
      this.minhaEscolaId = user.escola_id;
    } else {
      this.minhaEscolaId = null;
    }

    console.log('Usuário logado:', user);
    console.log('É superadmin?', this.isSuperAdmin);
    console.log('Minha escola ID:', this.minhaEscolaId);

    // 2. Configurar Formulário com base no Perfil
    if (this.isSuperAdmin) {
      // Cenário Superadmin: Carregar Escolas
      this.carregarEscolas();
      this.form.get('escola_id')?.setValidators(Validators.required);
    } else {
      // Cenário Admin/Secretária: Definir escola_id automaticamente
      if (this.minhaEscolaId !== null && this.minhaEscolaId !== undefined) {
        this.form.patchValue({ escola_id: this.minhaEscolaId });
        // Carregar turmas da MINHA escola
        this.carregarTurmas(this.minhaEscolaId);
      } else {
        console.error('Admin sem escola_id associado!');
        this.mensagemErro = 'Erro: seu usuário não está associado a uma escola.';
      }
    }

    // 3. Verificar Modo Edição
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEditMode = true;
      this.alunoId = Number(id);
      this.carregarDados(this.alunoId);
    }
  }

  // Apenas para Superadmin
  carregarEscolas() {
    this.escolaService.getEscolas().subscribe({
      next: (data) => {
        this.escolas = data;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Erro ao carregar escolas:', err);
        this.mensagemErro = 'Erro ao carregar lista de escolas.';
      }
    });
  }

  // Quando o Superadmin seleciona uma escola
  onEscolaChange() {
    const escolaIdSelecionada = this.form.get('escola_id')?.value;

    // Limpa a seleção de turma anterior
    this.form.patchValue({ turma_id: null });
    this.turmas = [];

    if (escolaIdSelecionada) {
      this.carregarTurmas(escolaIdSelecionada);
    }
  }

  carregarTurmas(escolaId: number) {
    console.log('Carregando turmas para escola ID:', escolaId);

    this.turmaService.getTurmas(escolaId).subscribe({
      next: (dados) => {
        console.log('Turmas carregadas:', dados);
        this.turmas = dados;
        this.cdr.detectChanges();

        if (dados.length === 0) {
          this.mensagemErro = 'Esta escola não possui turmas cadastradas.';
        }
      },
      error: (err) => {
        console.error('Erro ao carregar turmas:', err);
        this.mensagemErro = 'Erro ao carregar turmas. Verifique sua conexão.';
      }
    });
  }

  carregarDados(id: number) {
    this.alunoService.getAlunoById(id).subscribe({
      next: (aluno) => {
        this.form.patchValue({
          nome: aluno.nome,
          bi: aluno.bi,
          data_nascimento: aluno.data_nascimento,
          escola_id: aluno.escola_id,
          turma_id: aluno.turma_id
        });

        // Se for Superadmin em modo edição, carregar turmas da escola deste aluno
        if (this.isSuperAdmin && aluno.escola_id) {
          this.carregarTurmas(aluno.escola_id);
        }
      },
      error: (err) => {
        console.error('Erro ao carregar dados do aluno:', err);
        this.mensagemErro = 'Erro ao carregar dados do aluno.';
      }
    });
  }

  onSubmit() {
    if (this.form.valid) {
      const dados = this.form.value;

      // Para admin (não superadmin), garantir que escola_id está definido
      if (!this.isSuperAdmin && !dados.escola_id && this.minhaEscolaId !== null) {
        dados.escola_id = this.minhaEscolaId;
      }

      console.log('Dados a enviar:', dados);

      if (this.isEditMode && this.alunoId) {
        this.alunoService.atualizarAluno(this.alunoId, dados).subscribe({
          next: () => {
            alert('Aluno atualizado com sucesso!');
            this.router.navigate(['/lista-alunos']);
          },
          error: (err) => {
            console.error('Erro ao atualizar:', err);
            this.mensagemErro = 'Erro ao atualizar aluno.';
          }
        });
      } else {
        this.alunoService.matricularAluno(dados).subscribe({
          next: () => {
            this.mensagemSucesso = 'Aluno matriculado com sucesso!';
            // Reset parcial do formulário
            this.form.patchValue({
              nome: '',
              bi: '',
              data_nascimento: '',
              ativo: true,
              // Mantém escola_id e turma_id para facilitar matrículas em lote
            });
            setTimeout(() => this.mensagemSucesso = '', 3000);
          },
          error: (err) => {
            console.error('Erro ao criar:', err);
            this.mensagemErro = 'Erro ao matricular aluno. Verifique os dados.';
          }
        });
      }
    } else {
      this.mensagemErro = 'Por favor, preencha todos os campos obrigatórios.';
    }
  }
}
