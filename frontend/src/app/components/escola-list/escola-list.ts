import { ChangeDetectorRef, Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { EscolaService, Escola } from '../../services/escola.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-escola-list',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './escola-list.html'
})
export class EscolaList implements OnInit {
  escolaService = inject(EscolaService);
  authService = inject(AuthService);
  escolas = signal<Escola[]>([]); // 👈 sinal
  isSuperAdmin = signal(false);   // 👈 sinal (opcional)

  ngOnInit() {
    this.isSuperAdmin.set(this.authService.currentUser()?.perfil === 'superadmin');
    this.escolaService.getEscolas().subscribe(dados => {
      // console.log('📦 Escolas recebidas:', dados);
      this.escolas.set(dados); // 👈 atualiza o sinal
    });
  }

  trackById(index: number, item: Escola): number {
    return item.id!;
  }

  toggleStatus(escola: Escola) {
    if (!escola.id) return;
    this.escolaService.toggleEscolaStatus(escola.id).subscribe({
      next: (updated) => {
        // Atualizar o item no sinal (imutabilidade)
        this.escolas.update(list =>
          list.map(e => e.id === updated.id ? updated : e)
        );
      },
      error: (err) => {
        console.error('Erro ao alternar status', err);
        alert('Erro ao alterar estado da escola. Verifique se é superadmin.');
      }
    });
  }
}
