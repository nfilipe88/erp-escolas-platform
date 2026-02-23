import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardService, DashboardData } from '../../services/dashboard.service';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, NgxChartsModule],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css']
})
export class Dashboard implements OnInit {
  private dashboardService = inject(DashboardService);

  data = signal<DashboardData | null>(null);
  carregando = true;
  erro: string | null = null;

  // Configurações Gráficas
  view: [number, number] = [700, 300];
  colorScheme: any = { domain: ['#5AA454', '#A10A28', '#C7B42C', '#AAAAAA'] };

  ngOnInit() {
    this.carregarDados();
  }

  carregarDados() {
    this.carregando = true;
    this.dashboardService.getResumo()
      .pipe(finalize(() => this.carregando = false))
      .subscribe({
        next: (res) => this.data.set(res),
        error: (err) => this.erro = 'Não foi possível carregar o dashboard.'
      });
  }
}
