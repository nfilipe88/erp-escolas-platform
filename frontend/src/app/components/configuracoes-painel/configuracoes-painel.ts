import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { EscolaService, ConfiguracaoEscola } from '../../services/escola.service';

@Component({
  selector: 'app-configuracoes-painel',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './configuracoes-painel.html',
})
export class ConfiguracoesPainel implements OnInit {
  private escolaService = inject(EscolaService);

  config: ConfiguracaoEscola | null = null;
  salvando = false;
  sucesso = false;

  ngOnInit() {
    this.carregarDados();
  }

  carregarDados() {
    this.escolaService.getConfiguracao().subscribe(dados => {
      this.config = dados;
    });
  }

  salvar() {
    if (this.config) {
      this.salvando = true;
      this.sucesso = false;

      this.escolaService.updateConfiguracao(this.config).subscribe({
        next: (res) => {
          this.config = res; // Atualiza com o retorno do servidor
          this.salvando = false;
          this.sucesso = true;
          // Esconde a mensagem de sucesso após 3 segundos
          setTimeout(() => this.sucesso = false, 3000);
        },
        error: (err) => {
          console.error(err);
          this.salvando = false;
          alert('Erro ao salvar configurações.');
        }
      });
    }
  }
}
