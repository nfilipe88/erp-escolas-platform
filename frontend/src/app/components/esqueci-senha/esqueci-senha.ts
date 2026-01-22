import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-esqueci-senha',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './esqueci-senha.html',
  styleUrl: './esqueci-senha.css',
})
export class EsqueciSenha {
  authService = inject(AuthService);
  email = '';
  mensagem = '';
  loading = false;

  enviar() {
    this.loading = true;
    this.authService.esqueciSenha(this.email).subscribe({
      next: () => {
        this.mensagem = 'Verifique o seu email. Enviámos um link de recuperação.';
        this.loading = false;
      },
      error: () => {
        // Mesmo se der erro, mostramos a mesma msg por segurança ou "Tente novamente"
        this.mensagem = 'Verifique o seu email. Enviámos um link de recuperação.';
        this.loading = false;
      }
    });
  }
}
