import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { TurmaService, Turma } from '../../services/turma.service';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-turma-list',
  imports: [CommonModule, RouterLink],
  templateUrl: './turma-list.html',
  styleUrl: './turma-list.css',
})
export class TurmaList implements OnInit {
  private turmaService = inject(TurmaService);
  private cdr = inject(ChangeDetectorRef);
  turmas: Turma[] = [];

  ngOnInit() {
    this.carregarTurmas();
  }

  carregarTurmas() {
    // ✅ Chama sem parâmetro – o backend filtra automaticamente
    this.turmaService.getTurmas().subscribe(dados => {
      this.turmas = dados;
      this.cdr.detectChanges();
    });
  }
}
