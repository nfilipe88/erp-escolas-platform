import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FinanceiroService, Mensalidade } from '../../services/financeiro.service';
import { AlunoService, Aluno } from '../../services/aluno.service';

@Component({
  selector: 'app-aluno-recibo',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './aluno-recibo.html',
  styleUrl: './aluno-recibo.css'
})
export class AlunoRecibo implements OnInit {
  private route = inject(ActivatedRoute);
  private financeiroService = inject(FinanceiroService);
  private alunoService = inject(AlunoService);
  private cdr = inject(ChangeDetectorRef);

  mensalidade: Mensalidade | null = null;
  aluno: Aluno | null = null;
  dataHoje = new Date();

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.carregarDados(Number(id));
    }
  }

  carregarDados(id: number) {
    this.financeiroService.getMensalidadeById(id).subscribe(m => {
      this.mensalidade = m;
      // Assim que temos a mensalidade, buscamos o nome do aluno
      this.alunoService.getAlunoById(m.aluno_id!).subscribe(a => {
        this.aluno = a;
        this.cdr.detectChanges(); // <--- Força o Angular a pintar a tela AGORA
      });
    });
  }

  imprimir() {
    window.print();
  }
}
