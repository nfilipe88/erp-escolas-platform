import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { EscolaService, Escola } from '../../services/escola.service';

@Component({
  selector: 'app-escola-list',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './escola-list.html'
})
export class EscolaList implements OnInit {
  escolaService = inject(EscolaService);
  private cdr = inject(ChangeDetectorRef)
  escolas: Escola[] = [];

  ngOnInit() {
    this.escolaService.getEscolas().subscribe(dados => {
      this.escolas = dados,
      this.cdr.detectChanges();
    });
  }
}
