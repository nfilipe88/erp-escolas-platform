import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { HorarioService } from '../../services/horario.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-professor-aulas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './professor-aulas.html'
})
export class ProfessorAulas implements OnInit {
  horarioService = inject(HorarioService);
  router = inject(Router);

  aulasHoje: any[] = [];
  loading = true; // Para mostrar feedback visual

  // Controlo de Modal Fechar Aula
  aulaParaFechar: any = null;
  resumoAula: string = '';

  ngOnInit() {
    this.carregarMinhasAulas();
  }

  // IMPLEMENTAÇÃO REAL (Backend-First)
  carregarMinhasAulas() {
    this.loading = true;

    // Chama a rota dedicada que criámos no Backend
    this.horarioService.getMeuHorarioHoje().subscribe({
      next: (dados) => {
        this.aulasHoje = dados;
        this.loading = false;

        if (dados.length === 0) {
          console.log('Sem aulas para hoje.');
        }
      },
      error: (err) => {
        console.error('Erro ao carregar horário', err);
        this.loading = false;
        alert('Não foi possível carregar as suas aulas.');
      }
    });
  }

  // Validação Real de Tempo (Chama o Backend)
  tentarFazerChamada(aula: any) {
    this.horarioService.validarTempo(aula.id).subscribe({
      next: (res) => {
        if (res.pode) {
          // Navega para a chamada real passando o ID da turma
          this.router.navigate(['/chamada', aula.turma_id]);
        } else {
          alert(`🚫 Acesso Negado: ${res.msg}`);
        }
      },
      error: () => alert('Erro técnico ao validar horário.')
    });
  }

  abrirFecharAula(aula: any) {
    this.aulaParaFechar = aula;
    this.resumoAula = '';
  }

  confirmarFecho() {
    if (!this.resumoAula.trim()) {
      alert('Por favor, escreva um resumo da aula.');
      return;
    }

    this.horarioService.fecharDiario({
      horario_id: this.aulaParaFechar.id,
      resumo_aula: this.resumoAula
    }).subscribe({
      next: () => {
        alert('Aula terminada e diário enviado com sucesso! 📜');
        this.aulaParaFechar = null;
        // Recarregar para atualizar estado ou remover da lista
        // (Dependendo da tua lógica, podes querer esconder a aula fechada)
      },
      error: () => alert('Erro ao enviar diário.')
    });
  }
}
