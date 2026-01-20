import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { TurmaService } from '../../services/turma.service';

@Component({
  selector: 'app-turma-form',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './turma-form.html',
  styleUrl: './turma-form.css',
})
export class TurmaForm {
  private fb = inject(FormBuilder);
  private turmaService = inject(TurmaService);

  mensagemSucesso = '';

  // Opções para o select do turno
  turnos = ['Manhã', 'Tarde', 'Noite'];

  form: FormGroup = this.fb.group({
    nome: ['', Validators.required],       // Ex: 7ª A
    ano_letivo: ['2025', Validators.required], // Valor padrão 2025
    turno: ['Manhã', Validators.required],
    escola_id: [1, Validators.required]    // Fixo na escola 1
  });

  onSubmit() {
    if (this.form.valid) {
      this.turmaService.criarTurma(this.form.value).subscribe({
        next: (res) => {
          this.mensagemSucesso = `Turma "${res.nome}" criada!`;
          // Reinicia o form mantendo o ano e escola
          this.form.reset({
            ano_letivo: '2025',
            turno: 'Manhã',
            escola_id: 1
          });

          // Faz a mensagem desaparecer após 3 segundos
          setTimeout(() => this.mensagemSucesso = '', 3000);
        },
        error: (err) => alert('Erro ao criar turma')
      });
    }
  }
}
