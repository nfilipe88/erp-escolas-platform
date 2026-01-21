import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AlunoService, Boletim } from '../../services/aluno.service';

@Component({
  selector: 'app-aluno-boletim',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './aluno-boletim.html',
  styleUrl: './aluno-boletim.css'
})
export class AlunoBoletim implements OnInit {
  private route = inject(ActivatedRoute);
  private alunoService = inject(AlunoService);
  private cdr = inject(ChangeDetectorRef);

  boletim: Boletim | null = null;
  dataHoje = new Date();

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.alunoService.getBoletim(Number(id)).subscribe(dados => {
        this.boletim = dados;
        this.cdr.detectChanges();
      });
    }
  }

  getNota(notas: any[], trimestre: string): string {
    const nota = notas.find(n => n.trimestre === trimestre);
    return nota ? nota.valor.toString() : '-';
  }

  // Função auxiliar para imprimir
  imprimir() {
    window.print();
  }
}
