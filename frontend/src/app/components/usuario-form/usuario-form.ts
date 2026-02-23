import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { UsuarioCreate, UsuarioService } from '../../services/usuario.service';
import { AuthService } from '../../services/auth.service';
import { EscolaService } from '../../services/escola.service';
import { Role, RoleService } from '../../services/role.service';

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
  roleService = inject(RoleService);
  router = inject(Router);

  isSuperAdmin = false;
  escolas: any[] = [];
  rolesDisponiveis: Role[] = [];

  usuario: UsuarioCreate = {
    nome: '',
    email: '',
    senha: '',
    roles: [],
    escola_id: null,
    ativo: true
  };

  ngOnInit() {
    const user = this.authService.getUsuarioLogado();
    this.isSuperAdmin = user?.roles.some(r => r.name === 'superadmin') ?? false;

    // Carregar lista de roles disponíveis
    this.roleService.getRoles().subscribe(data => {
      this.rolesDisponiveis = data;
    });

    if (this.isSuperAdmin) {
      this.escolaService.getEscolas().subscribe(data => {
        this.escolas = data;
      });
    }
  }

  // Gerencia a seleção/deseleção de roles
  toggleRole(roleId: number, event: Event) {
    const checked = (event.target as HTMLInputElement).checked;
    if (checked) {
      this.usuario.roles.push(roleId);
    } else {
      this.usuario.roles = this.usuario.roles.filter(id => id !== roleId);
    }
  }

  salvar() {
    if (!this.usuario.nome || !this.usuario.email || !this.usuario.senha) {
      alert('Preencha todos os campos obrigatórios.');
      return;
    }

    // Validação para superadmin: se não for criar superadmin, precisa de escola_id
    const roleSuperAdmin = this.rolesDisponiveis.find(r => r.name === 'superadmin');
    const isCreatingSuperAdmin = roleSuperAdmin && this.usuario.roles.includes(roleSuperAdmin.id);

    if (this.isSuperAdmin && !isCreatingSuperAdmin && !this.usuario.escola_id) {
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
