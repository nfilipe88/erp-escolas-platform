import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HorarioService } from '../../services/horario.service';

@Component({
  selector: 'app-professor-aulas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './professor-aulas.html'
})
export class ProfessorAulas implements OnInit {
  private horarioService = inject(HorarioService);
  private router = inject(Router);

  aulasHoje: any[] = [];
  loading = true;
  dataHoje = new Date(); // ← necessário no template

  // Controlo do modal de fecho
  aulaParaFechar: any = null;
  resumoAula = '';

  ngOnInit() {
    this.carregarAulas();
  }

  carregarAulas() {
    this.loading = true;
    this.horarioService.getMeuHorarioHoje().subscribe({
      next: (dados) => {
        this.aulasHoje = dados;
        this.loading = false;
      },
      error: (err) => {
        console.error('Erro ao carregar aulas:', err);
        this.loading = false;
        alert('Não foi possível carregar as suas aulas. Tente novamente.');
      }
    });
  }

  fazerChamada(aula: any) {
    // Antes de navegar, valida se o professor pode fazer chamada agora
    this.horarioService.validarTempo(aula.id).subscribe({
      next: (res) => {
        if (res.pode) {
          // Redireciona para a página de chamada da turma
          this.router.navigate(['/chamada', aula.turma_id]);
        } else {
          alert(`⏰ Acesso negado: ${res.msg}`);
        }
      },
      error: () => alert('Erro ao validar horário.')
    });
  }

  abrirModalFechar(aula: any) {
    this.aulaParaFechar = aula;
    this.resumoAula = '';
  }

  cancelarFecho() {
    this.aulaParaFechar = null;
    this.resumoAula = '';
  }

  confirmarFechoAula() {
    if (!this.resumoAula.trim()) {
      alert('Por favor, escreva um resumo da aula.');
      return;
    }

    this.horarioService.fecharDiario({
      horario_id: this.aulaParaFechar.id,
      resumo_aula: this.resumoAula
    }).subscribe({
      next: () => {
        alert('✅ Diário fechado com sucesso!');
        this.cancelarFecho();
        // Opcional: recarregar a lista para remover a aula fechada (se o backend retornar só não fechadas)
        this.carregarAulas();
      },
      error: (err) => {
        console.error('Erro ao fechar diário:', err);
        alert('Erro ao fechar diário. Tente novamente.');
      }
    });
  }
}
