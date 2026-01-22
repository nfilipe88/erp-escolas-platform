import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
authService = inject(AuthService);
  router = inject(Router);

  email = '';
  senha = '';
  erro = '';
  loading = false;

  entrar() {
    this.loading = true;
    this.erro = '';

    this.authService.login(this.email, this.senha).subscribe({
      next: () => {
        this.router.navigate(['/dashboard']); // Sucesso! Vai para o Dashboard
      },
      error: (err) => {
        console.error(err);
        this.erro = 'Email ou senha incorretos.';
        this.loading = false;
      }
    });
  }
}
