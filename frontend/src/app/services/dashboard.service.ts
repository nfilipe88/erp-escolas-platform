import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment.development';

export interface DashboardCard {
  titulo: string;
  valor: string | number;
  cor: string;
  icon: string;
}

export interface DashboardData {
  perfil: string;
  cards: DashboardCard[];
  graficos: any; // Tipagem flexível para gráficos variados
}

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  getResumo(): Observable<DashboardData> {
    return this.http.get<DashboardData>(`${this.apiUrl}/dashboard/resumo`);
  }
}
