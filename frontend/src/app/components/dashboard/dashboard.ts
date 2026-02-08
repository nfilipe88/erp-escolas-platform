import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { DashboardService, DashboardStats } from '../../services/dashboard.service';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit {
  private dashboardService = inject(DashboardService);
  private cdr = inject(ChangeDetectorRef);
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private router = inject(Router);

  // Dados do utilizador logado
  perfil: string = '';
  nomeUsuario: string = '';
  escolaId: number | null = null;

  // Dados do dashboard do Admin
  stats: DashboardStats | null = null;
  dataHoje = new Date();

  // Dados do Professor
  minhasAulas: any[] = [];
  carregando: boolean = true;

  ngOnInit() {
    console.log('Dashboard iniciando...'); // DEBUG

    // 1. Obter usuário logado
    const user = this.authService.getUsuarioLogado();
    console.log('Usuário logado:', user); // DEBUG

    if (!user) {
      console.warn('Nenhum usuário logado, redirecionando para login');
      this.router.navigate(['/login']);
      return;
    }

    this.perfil = user.perfil || '';
    this.nomeUsuario = user.nome || 'Utilizador';
    this.escolaId = user.escola_id;

    console.log('Perfil detectado:', this.perfil); // DEBUG

    // 2. Carregar dados consoante o perfil

    if (this.perfil === 'admin' || this.perfil === 'secretaria') {
      // Trata Secretaria igual a Admin (mostra stats)
      this.carregarDashboardAdmin();
    } else if (this.perfil === 'superadmin') {
      this.carregarDashboardAdmin(); // Superadmin também vê stats
    } else if (this.perfil === 'professor') {
      this.carregarDashboardProfessor();
    } else {
      console.warn('Perfil não reconhecido:', this.perfil);
    }
  }

  carregarDashboardAdmin() {
    console.log('Carregando dashboard admin...'); // DEBUG
    this.dashboardService.getStats().subscribe({
      next: (data) => {
        console.log('Stats recebidos:', data); // DEBUG
        this.stats = data;
        this.carregando = false;
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Erro ao carregar stats:', error);
        this.carregando = false;
        this.cdr.detectChanges();
      }
    });
  }

  carregarDashboardProfessor() {
    console.log('Carregando dashboard professor...'); // DEBUG
    this.http.get<any[]>('http://127.0.0.1:8000/minhas-aulas').subscribe({
      next: (data) => {
        console.log('Aulas recebidas:', data); // DEBUG
        this.minhasAulas = data;
        this.carregando = false;
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Erro ao carregar aulas:', error);
        this.carregando = false;
        this.cdr.detectChanges();
      }
    });
  }
}
