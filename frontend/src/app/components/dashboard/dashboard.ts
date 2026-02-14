import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { DashboardService, DashboardStats } from '../../services/dashboard.service';
import { AtribuicaoService } from '../../services/atribuicao.service'; // ← import
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit {
  private dashboardService = inject(DashboardService);
  private atribuicaoService = inject(AtribuicaoService); // ← inject
  private authService = inject(AuthService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);

  perfil: string = '';
  nomeUsuario: string = '';
  escolaId: number | null = null;

  stats: DashboardStats | null = null;
  dataHoje = new Date();

  minhasAulas: any[] = [];
  carregando: boolean = true;

  ngOnInit() {
    const user = this.authService.getUsuarioLogado();
    if (!user) {
      this.router.navigate(['/login']);
      return;
    }

    this.perfil = user.perfil || '';
    this.nomeUsuario = user.nome || 'Utilizador';
    this.escolaId = user.escola_id;

    if (this.perfil === 'admin' || this.perfil === 'secretaria' || this.perfil === 'superadmin') {
      this.carregarDashboardAdmin();
    } else if (this.perfil === 'professor') {
      this.carregarDashboardProfessor();
    }
  }

  carregarDashboardAdmin() {
    this.dashboardService.getStats().subscribe({
      next: (data) => {
        this.stats = data;
        this.carregando = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.carregando = false;
        this.cdr.detectChanges();
      }
    });
  }

  carregarDashboardProfessor() {
    this.atribuicaoService.getMinhasAulas().subscribe({  // ← usa o serviço
      next: (data) => {
        this.minhasAulas = data;
        this.carregando = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.carregando = false;
        this.cdr.detectChanges();
      }
    });
  }
}
