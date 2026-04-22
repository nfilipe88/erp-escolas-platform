import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { EscolaService, ConfiguracaoEscola } from '../../services/escola.service';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-configuracoes-painel',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './configuracoes-painel.html',
})
export class ConfiguracoesPainel implements OnInit {
  private escolaService = inject(EscolaService);
  private route = inject(ActivatedRoute);

  config: ConfiguracaoEscola | null = null;
  salvando = false;
  sucesso = false;

  ngOnInit() {
    this.carregarDados();

    // Apanhamos o ID se ele vier na rota
    const queryEscolaId = this.route.snapshot.queryParamMap.get('escola_id');

    // Usamos o mesmo método flexível para tudo
    this.escolaService.getConfiguracoes(queryEscolaId).subscribe({
      next: (dados) => this.config = dados,
      error: (err) => console.error("Erro ao carregar configurações", err)
    });
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
