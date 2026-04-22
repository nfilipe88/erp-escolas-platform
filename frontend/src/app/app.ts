import { Component, computed, inject, signal } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from './services/auth.service';
import { CommonModule } from '@angular/common';
import {alunoRoutes} from './routers/aluno.routers';
import { professorRoutes } from './routers/professor.routers';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  authService = inject(AuthService);
  private router = inject(Router);

  // Sinal para controlar se o menu lateral está aberto (mobile)
  sidebarOpen = signal(false);

  // Computar o utilizador atual automaticamente
  user = this.authService.currentUser;

  // Lógica de Menus baseada no Perfil (Role)
  menus = computed(() => {
    const u = this.user();
    if (!u) return [];

    const roles = u.roles.map((r: { name: string; }) => r.name.toLowerCase());
    // DEBUG: Isto vai imprimir na consola do navegador o que está a chegar do Backend!
    console.log("=== ROLES DETETADOS PELO ANGULAR ===", roles);
    // Menus comuns a todos
    const menusBase = [
      { label: 'Dashboard', icon: 'home', route: '/dashboard' }
    ];

    // Menus de Administrador
    if (roles.includes('superadmin')) {
      return [
        ...menusBase,
        { label: 'Escolas', icon: 'school', route: '/escolas' },
        { label: 'Alunos', icon: 'face', route: '/lista-alunos' },
        { label: 'Turmas', icon: 'class', route: '/lista-turmas' },
        { label: 'Disciplinas', icon: 'book', route: '/disciplinas' },
        // { label: 'Alunos', icon: 'face', route: '/alunos' }, // Rota corrigida para /alunos
        { label: 'Professores', icon: 'people', route: '/professores' },
        { label: 'Financeiro', icon: 'payments', route: '/financeiro' },
        { label: 'Utilizadores', icon: 'admin_panel_settings', route: '/usuarios' },
        // { label: 'Configurações', icon: 'settings', route: '/configuracoes' }
      ];
    }

    // Menus de Administrador
    if (roles.includes('admin')) {
      return [
        ...menusBase,
        { label: 'Turmas', icon: 'class', route: '/lista-turmas' },
        { label: 'Disciplinas', icon: 'book', route: '/disciplinas' },
        { label: 'Alunos', icon: 'face', route: '/alunos' }, // Rota corrigida para /alunos
        { label: 'Professores', icon: 'people', route: '/professores' },
        { label: 'Financeiro', icon: 'payments', route: '/financeiro' },
        { label: 'Utilizadores', icon: 'admin_panel_settings', route: '/usuarios' },
        // { label: 'Configurações', icon: 'settings', route: '/configuracoes' }
      ];
    }

    // Menus de Professor
    if (roles.includes('professor')) {
      return [
        ...menusBase,
        { label: 'Minhas Turmas', icon: 'class', route: '/minhas-turmas' },
        { label: 'Lançar Notas', icon: 'edit_note', route: '/lancar-notas' },
        { label: 'Ponto', icon: 'timer', route: '/ponto' }
      ];
    }

    // Menus de Secretaria
    if (roles.includes('secretaria')) {
      return [
        ...menusBase,
        { label: 'Matrículas', icon: 'how_to_reg', route: '/alunos' },
        { label: 'Turmas', icon: 'class', route: '/turmas' },
        { label: 'Pagamentos', icon: 'attach_money', route: '/financeiro' }
      ];
    }

    // Menus de Aluno
    if (roles.includes('aluno')) {
      return [
        ...menusBase,
        { label: 'Minhas Notas', icon: 'grade', route: '/minhas-notas' },
        { label: 'Financeiro', icon: 'payments', route: '/financeiro' }
      ];
    }

    // Se for Visitante, mostra algo amigável mas restrito
    if (roles.includes('visitante')) {
      return [
        ...menusBase,
        { label: 'Informações', icon: 'info', route: '/info-visitante' }
      ];
    }

    // Fallback (Aluno ou User simples)
    return menusBase;
  });

  toggleSidebar() {
    this.sidebarOpen.update(v => !v);
  }

  logout() {
    this.authService.logout();
  }
}
