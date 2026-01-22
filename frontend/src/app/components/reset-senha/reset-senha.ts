import { CommonModule } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-reset-senha',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './reset-senha.html',
  styleUrl: './reset-senha.css',
})
export class ResetSenha implements OnInit {
  route = inject(ActivatedRoute);
  router = inject(Router);
  authService = inject(AuthService);

  token = '';
  novaSenha = '';
  confirmarSenha = '';
  erro = '';
  sucesso = false;

  ngOnInit() {
    // Pega o token da URL (?token=...)
    this.token = this.route.snapshot.queryParamMap.get('token') || '';
  }

  alterar() {
    if (this.novaSenha !== this.confirmarSenha) {
      this.erro = 'As senhas não coincidem.';
      return;
    }

    this.authService.resetSenha(this.token, this.novaSenha).subscribe({
      next: () => {
        this.sucesso = true;
        setTimeout(() => this.router.navigate(['/login']), 3000); // Redireciona após 3s
      },
      error: (err) => {
        this.erro = err.error.detail || 'Token inválido ou expirado.';
      }
    });
  }
}
