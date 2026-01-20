import { Component, inject, OnInit } from '@angular/core';
import { TurmaService, Turma } from '../../services/turma.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-turma-list',
  imports: [CommonModule],
  templateUrl: './turma-list.html',
  styleUrl: './turma-list.css',
})
export class TurmaList implements OnInit {
  private turmaService = inject(TurmaService);
  turmas: Turma[] = [];

  ngOnInit() {
    this.carregarTurmas();
  }

  carregarTurmas() {
    // Busca turmas da Escola ID 1
    this.turmaService.getTurmas(1).subscribe(dados => {
      this.turmas = dados;
    });
  }
}
