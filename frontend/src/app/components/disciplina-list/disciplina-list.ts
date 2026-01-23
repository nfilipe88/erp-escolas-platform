import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DisciplinaService, Disciplina } from '../../services/disciplina.service';

@Component({
  selector: 'app-disciplina-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './disciplina-list.html'
})
export class DisciplinaList implements OnInit {
  private service = inject(DisciplinaService);
  private cdr= inject(ChangeDetectorRef);

  disciplinas: Disciplina[] = [];
  nova: Disciplina = { nome: '', codigo: '', carga_horaria: 80 };

  ngOnInit() {
    this.carregar();
  }

  carregar() {
    this.service.getDisciplinas().subscribe(d => {
      this.disciplinas = d;
      this.cdr.detectChanges();
    });
  }

  adicionar() {
    this.service.criar(this.nova).subscribe(() => {
      this.carregar(); // Recarrega a tabela
      this.nova = { nome: '', codigo: '', carga_horaria: 80 }; // Limpa o form
    });
  }
}
