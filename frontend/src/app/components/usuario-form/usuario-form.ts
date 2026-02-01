import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { UsuarioService } from '../../services/usuario.service';

@Component({
  selector: 'app-usuario-form',
  imports: [CommonModule, FormsModule],
  templateUrl: './usuario-form.html',
  styleUrl: './usuario-form.css',
})
export class UsuarioForm {
  usuarioService = inject(UsuarioService);
  router = inject(Router);

  isSuperAdmin = false;

  usuario = {
    nome: '',
    email: '',
    senha: '',
    perfil: 'professor', // Padrão
    ativo: true
  };

  salvar() {
    if (!this.usuario.nome || !this.usuario.email || !this.usuario.senha) {
      alert('Preencha todos os campos obrigatórios.');
      return;
    }

    this.usuarioService.createUsuario(this.usuario).subscribe({
      next: () => {
        alert('Funcionário criado com sucesso! 📧');
        this.router.navigate(['/usuarios']);
      },
      error: (err) => {
        console.error(err);
        alert('Erro ao criar. O email já pode existir.');
      }
    });
  }
}
