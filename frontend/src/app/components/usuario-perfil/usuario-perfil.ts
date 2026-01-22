import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-usuario-perfil',
  imports: [CommonModule, FormsModule],
  templateUrl: './usuario-perfil.html',
  styleUrl: './usuario-perfil.css',
})
export class UsuarioPerfil {
authService = inject(AuthService);

  senhaAtual = '';
  novaSenha = '';
  mensagem = '';
  erro = '';

  salvar() {
    this.mensagem = '';
    this.erro = '';

    this.authService.alterarSenha(this.senhaAtual, this.novaSenha).subscribe({
      next: () => {
        this.mensagem = 'Senha alterada com sucesso!';
        this.senhaAtual = '';
        this.novaSenha = '';
      },
      error: (err) => {
        this.erro = err.error.detail || 'Erro ao alterar senha.';
      }
    });
  }
}
