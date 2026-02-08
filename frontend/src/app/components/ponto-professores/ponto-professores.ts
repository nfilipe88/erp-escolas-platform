import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
// Removemos a importação do HttpClient
import { PresencaService } from '../../services/presenca.service';

@Component({
  selector: 'app-ponto-professores',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './ponto-professores.html'
})
export class PontoProfessores implements OnInit {
  // Injetamos o Serviço em vez do HttpClient
  private presencaService = inject(PresencaService);

  dataSelecionada: string = new Date().toISOString().split('T')[0];
  professores: any[] = [];
  loading = false;

  ngOnInit() {
    this.carregarPonto();
  }

  carregarPonto() {
    this.loading = true;
    // Chamada via Serviço
    this.presencaService.getPontoProfessores(this.dataSelecionada)
      .subscribe({
        next: (data) => {
          this.professores = data;
          this.loading = false;
        },
        error: (err) => {
          console.error(err);
          this.loading = false;
          alert('Erro ao carregar lista de professores.');
        }
      });
  }

  alternarPresenca(prof: any) {
    prof.presente = !prof.presente;
  }

  salvar() {
    const payload = {
      data: this.dataSelecionada,
      lista: this.professores
    };

    // Chamada via Serviço
    this.presencaService.salvarPontoProfessores(payload).subscribe({
      next: () => alert('Assiduidade dos professores registada! 📋'),
      error: (err) => {
        console.error(err);
        alert('Erro ao salvar ponto.');
      }
    });
  }
}
