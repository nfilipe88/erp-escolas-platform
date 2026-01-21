import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { DashboardService, DashboardStats } from '../../services/dashboard.service';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit {
  private dashboardService = inject(DashboardService);
  private cdr = inject(ChangeDetectorRef);

  stats: DashboardStats | null = null;
  dataHoje = new Date();

  ngOnInit() {
    this.carregarStats();
  }

  carregarStats() {
    this.dashboardService.getStats().subscribe(dados => {
      this.stats = dados;
      this.cdr.detectChanges();
    });
  }
}
