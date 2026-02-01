import { CommonModule } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { TurmaService } from '../../services/turma.service';
import { AuthService } from '../../services/auth.service';
import { EscolaService } from '../../services/escola.service';

@Component({
  selector: 'app-turma-form',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './turma-form.html',
  styleUrl: './turma-form.css',
})
export class TurmaForm implements OnInit {
  private fb = inject(FormBuilder);
  private turmaService = inject(TurmaService);
  private escolaService = inject(EscolaService);
  private authService = inject(AuthService);

  escolas: any[] = [];
  isSuperAdmin = false;
  mensagemSucesso = '';

  // Opções para o select do turno
  turnos = ['Manhã', 'Tarde', 'Noite'];

  form: FormGroup = this.fb.group({
    nome: ['', Validators.required],
    ano_letivo: ['2025', Validators.required],
    turno: ['Manhã', Validators.required],
    escola_id: [null] // Opcional (só usado se for Superadmin)
  });

  ngOnInit() {
    // 1. Verificar Perfil
    const usuario = this.authService.getUsuarioLogado();
    this.isSuperAdmin = usuario?.perfil === 'superadmin';

    // 2. Se for Superadmin, buscar lista de escolas para o Select
    if (this.isSuperAdmin) {
      this.escolaService.getEscolas().subscribe(data => {
        this.escolas = data;
        // Adicionar validador obrigatório dinamicamente
        this.form.get('escola_id')?.setValidators(Validators.required);
        this.form.get('escola_id')?.updateValueAndValidity();
      });
    }
  }

  onSubmit() {
    if (this.form.valid) {
      this.turmaService.criarTurma(this.form.value).subscribe({
        next: (res) => {
          this.mensagemSucesso = `Turma "${res.nome}" criada com sucesso!`;
          this.form.reset({
            ano_letivo: '2025',
            turno: 'Manhã',
            escola_id: null
          });
          setTimeout(() => this.mensagemSucesso = '', 3000);
        },
        error: (err) => alert('Erro ao criar turma. Verifique os dados.')
      });
    }
  }
}
