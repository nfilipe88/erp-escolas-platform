import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { EscolaService, EscolaDetalhes } from '../../services/escola.service';

@Component({
  selector: 'app-escola-detail',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './escola-detail.html'
})
export class EscolaDetail implements OnInit {
  route = inject(ActivatedRoute);
  escolaService = inject(EscolaService);
  private cdr=inject(ChangeDetectorRef)
  escola: EscolaDetalhes | null = null;

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.escolaService.getEscolaDetalhes(Number(id)).subscribe(dados => {
        this.escola = dados;
        this.cdr.detectChanges();
      });
    }
  }
}
