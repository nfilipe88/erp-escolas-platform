import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { AlunoService, Aluno } from '../../services/aluno.service';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-aluno-form',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './aluno-form.html',
  styleUrl: './aluno-form.css',
})
export class AlunoForm {
  private fb = inject(FormBuilder);
  private alunoService = inject(AlunoService);
  private route = inject(ActivatedRoute); // Para ler o ID da URL
  private router = inject(Router);        // Para navegar depois de salvar

  isEditMode = false;
  alunoId: number | null = null;

  mensagemSucesso = '';
  mensagemErro = '';

  form: FormGroup = this.fb.group({
    nome: ['', [Validators.required, Validators.minLength(3)]],
    bi: ['', [Validators.required]],
    data_nascimento: ['', Validators.required],
    escola_id: [1, Validators.required] // Fixo na escola 1 por enquanto
  });

  ngOnInit() {
    // Verifica se existe um ID na URL (ex: /editar-aluno/1)
    const id = this.route.snapshot.paramMap.get('id');

    if (id) {
      this.isEditMode = true;
      this.alunoId = Number(id);
      this.carregarDados(this.alunoId);
    }
  }

  carregarDados(id: number) {
    this.alunoService.getAlunoById(id).subscribe(aluno => {
      // Preenche o formulário com os dados do banco
      this.form.patchValue({
        nome: aluno.nome,
        bi: aluno.bi,
        data_nascimento: aluno.data_nascimento,
        escola_id: aluno.escola_id
      });
    });
  }

  onSubmit() {
    if (this.form.valid) {
      const dados = this.form.value;

      if (this.isEditMode && this.alunoId) {
        // --- MODO ATUALIZAR ---
        this.alunoService.atualizarAluno(this.alunoId, dados).subscribe({
          next: () => {
            alert('Aluno atualizado com sucesso!');
            this.router.navigate(['/lista-alunos']); // Volta para a lista
          },
          error: (err) => this.mensagemErro = 'Erro ao atualizar.'
        });
      } else {
        // --- MODO CRIAR (O teu código antigo) ---
        this.alunoService.matricularAluno(dados).subscribe({
          next: (res) => {
             this.mensagemSucesso = `Aluno criado!`;
             this.form.reset({ escola_id: 1 });
          },
          error: (err) => this.mensagemErro = 'Erro ao criar.'
        });
      }
    }
  }
}
