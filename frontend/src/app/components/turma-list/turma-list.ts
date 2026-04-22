import { ChangeDetectorRef, Component, inject, OnInit, signal } from '@angular/core';
import { TurmaService, Turma } from '../../services/turma.service';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-turma-list',
  imports: [CommonModule, RouterLink],
  templateUrl: './turma-list.html',
  styleUrl: './turma-list.css',
})
export class TurmaList implements OnInit {
  private turmaService = inject(TurmaService);
  authService = inject(AuthService);
  turmas = signal<Turma[]>([]);
  isSuperAdmin=signal(false);

  ngOnInit() {
    this.carregarTurmas();
  }

  trackById(index: number, item: Turma): number {
    return item.id!;
  }

  carregarTurmas() {
    // ✅ Chama sem parâmetro – o backend filtra automaticamente
    this.isSuperAdmin.set(this.authService.currentUser().perfil==='superadmin');

    this.turmaService.getTurmas().subscribe(dados => {
      console.log('Escolas recebidas', dados);
      this.turmas.set(dados);
    });
  }
}
