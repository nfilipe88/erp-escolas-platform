import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators, FormGroup } from '@angular/forms';
import { EscolaService, Escola } from '../../services/escola.service';

@Component({
  selector: 'app-escola-form',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './escola-form.html',
  styleUrl: './escola-form.css',
})
export class EscolaForm {
  private fb = inject(FormBuilder);
  private escolaService = inject(EscolaService);

  mensagemSucesso = '';
  mensagemErro = '';

  // Definição do formulário e validações
  form: FormGroup = this.fb.group({
    nome: ['', [Validators.required, Validators.minLength(3)]],
    slug: ['', [Validators.required, Validators.pattern('^[a-z0-9-]+$')]], // Só letras minúsculas e hífens
    endereco: ['']
  });

  onSubmit() {
    if (this.form.valid) {
      const novaEscola: Escola = this.form.value;

      this.escolaService.criarEscola(novaEscola).subscribe({
        next: (res) => {
          this.mensagemSucesso = `Escola "${res.nome}" criada com sucesso! (ID: ${res.id})`;
          this.mensagemErro = '';
          this.form.reset(); // Limpa o formulário
        },
        error: (err) => {
          console.error(err);
          this.mensagemErro = 'Erro ao criar escola. Verifica se o Slug já existe.';
          this.mensagemSucesso = '';
        }
      });
    }
  }
}
