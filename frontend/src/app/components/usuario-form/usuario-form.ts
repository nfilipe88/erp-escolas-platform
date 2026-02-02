import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { UsuarioService } from '../../services/usuario.service';
import { AuthService } from '../../services/auth.service';
import { EscolaService } from '../../services/escola.service'; // Importar serviço de escolas

@Component({
  selector: 'app-usuario-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './usuario-form.html'
})
export class UsuarioForm implements OnInit {
  usuarioService = inject(UsuarioService);
  authService = inject(AuthService);
  escolaService = inject(EscolaService);
  router = inject(Router);

  isSuperAdmin = false;
  escolas: any[] = [];

  usuario = {
    nome: '',
    email: '',
    senha: '',
    perfil: 'professor',
    escola_id: null, // Novo campo opcional
    ativo: true
  };

  ngOnInit() {
    // 1. Verificar quem está logado
    const user = this.authService.getUsuarioLogado();
    this.isSuperAdmin = user?.perfil === 'superadmin';

    // 2. Se for Superadmin, carregar lista de escolas
    if (this.isSuperAdmin) {
      this.escolaService.getEscolas().subscribe(data => {
        this.escolas = data;
      });
    }
  }

  salvar() {
    // Validação Básica
    if (!this.usuario.nome || !this.usuario.email || !this.usuario.senha) {
      alert('Preencha todos os campos obrigatórios.');
      return;
    }

    // Validação Específica para Superadmin
    if (this.isSuperAdmin && this.usuario.perfil !== 'superadmin' && !this.usuario.escola_id) {
      alert('Como Superadmin, deve selecionar uma escola para criar este tipo de utilizador.');
      return;
    }

    this.usuarioService.createUsuario(this.usuario).subscribe({
      next: () => {
        alert('Funcionário criado com sucesso! 📧');
        this.router.navigate(['/usuarios']);
      },
      error: (err) => {
        console.error(err);
        alert('Erro ao criar. Verifique os dados ou se o email já existe.');
      }
    });
  }
}
