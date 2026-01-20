import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { AlunoService, Aluno } from '../../services/aluno.service';
import { CommonModule, DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-aluno-list',
  imports: [CommonModule, DatePipe, RouterLink],
  templateUrl: './aluno-list.html',
  styleUrl: './aluno-list.css',
})
export class AlunoList implements OnInit {
  private alunoService = inject(AlunoService);
  private cdr = inject(ChangeDetectorRef);

  alunos: Aluno[] = [];
  escolaId = 1; // Fixo para teste

  ngOnInit() {
    this.carregarAlunos();
  }

  carregarAlunos() {
    this.alunoService.getAlunos(this.escolaId).subscribe({
      next: (dados) => {
        console.log('Dados recebidos:', dados); // Para confirmares na consola
        this.alunos = dados;
        this.cdr.detectChanges(); // <--- Força o Angular a pintar a tela AGORA
      },
      error: (erro) => {
        console.error('Erro ao buscar alunos', erro);
      }
    });
  }

  deletar(id: number) {
    if (confirm("Tens a certeza que queres apagar este aluno?")) {
      this.alunoService.removerAluno(id).subscribe({
        next: () => {
          // Remove da lista visualmente sem precisar recarregar a página
          this.alunos = this.alunos.filter(a => a.id !== id);
        },
        error: (err) => alert("Erro ao apagar aluno.")
      })
    }
  }
}
