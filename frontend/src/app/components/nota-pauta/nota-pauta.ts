import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router'; // Adicionar RouterLink
import { AlunoService, Aluno } from '../../services/aluno.service';
import { TurmaService, Turma } from '../../services/turma.service';
import { NotaService, Nota } from '../../services/nota.service';
import { forkJoin } from 'rxjs'; // Importante para o "Salvar Tudo"
import { Disciplina } from '../../services/disciplina.service';

@Component({
  selector: 'app-nota-pauta',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './nota-pauta.html',
  styleUrl: './nota-pauta.css'
})
export class NotaPauta implements OnInit {
  private route = inject(ActivatedRoute);
  private alunoService = inject(AlunoService);
  private turmaService = inject(TurmaService);
  private notaService = inject(NotaService);
  private cdr = inject(ChangeDetectorRef);

  turmaId!: number;
  turma!: Turma; // Para mostrar o nome no cabeçalho azul
  disciplinas: Disciplina[] = [];
  alunos: Aluno[] = [];

  // Variáveis de Controlo
  disciplinaSelecionadaId: number | null = null;
  trimestreSelecionado = '1º Trimestre';

  // Estado das Notas
  notasTemporarias: { [alunoId: number]: number } = {};    // O que está no input agora
  notasOriginais: { [alunoId: number]: number } = {};      // O que veio do banco (para comparar)
  arquivosTemporarios: { [alunoId: number]: File } = {};
  arquivosExistentes: { [alunoId: number]: string } = {};  // URL dos ficheiros já salvos
  loading = false; // Para mostrar feedback no botão Salvar Tudo

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('turmaId');
    if (id) {
      this.turmaId = Number(id);
      this.carregarDadosIniciais();
    }
  }

  carregarDadosIniciais() {
    // 1. Carrega Detalhes da Turma (para o cabeçalho azul)
    this.turmaService.getTurmaById(this.turmaId).subscribe(t => {
      this.turma = t;
      this.cdr.detectChanges();
    });

    // 2. Carrega Disciplinas
    this.turmaService.getDisciplinasByTurma(this.turmaId).subscribe(data => {
      this.disciplinas = data;
      this.cdr.detectChanges();
    });

    // 3. Carrega Alunos
    this.alunoService.getAlunosPorTurma(this.turmaId).subscribe(data => {
      this.alunos = data;
      this.cdr.detectChanges();
    });
  }

  // --- NOVA LÓGICA: Disparada quando mudas a Disciplina ou o Trimestre ---
  aoMudarFiltro() {
    // 1. Limpa tudo visualmente primeiro
    this.notasTemporarias = {};
    this.notasOriginais = {};
    this.arquivosTemporarios = {};
    this.arquivosExistentes = {};

    if (!this.disciplinaSelecionadaId) return;

    // 2. Busca as notas que já existem no banco
    this.notaService.getNotasPorDisciplina(this.disciplinaSelecionadaId).subscribe(notas => {
      // Filtra apenas notas deste trimestre
      const notasDoTrimestre = notas.filter(n => n.trimestre === this.trimestreSelecionado);

      // Preenche os inputs
      notasDoTrimestre.forEach(nota => {
        this.notasTemporarias[nota.aluno_id] = nota.valor;
        this.notasOriginais[nota.aluno_id] = nota.valor; // Guarda cópia para saber se mudou

        if (nota.arquivo_url) {
          this.arquivosExistentes[nota.aluno_id] = nota.arquivo_url;
        }
      });
    });
  }

  onFileSelected(event: any, alunoId: number) {
    const file: File = event.target.files[0];
    if (file) {
      this.arquivosTemporarios[alunoId] = file;
    }
  }

  // Verifica se o botão individual deve estar habilitado
  podeSalvar(alunoId: number): boolean {
    const notaAtual = this.notasTemporarias[alunoId];
    const notaOriginal = this.notasOriginais[alunoId];
    const temArquivoNovo = !!this.arquivosTemporarios[alunoId];

    // Habilita se: (Tem nota escrita) E ( (Nota mudou) OU (Tem arquivo novo) OU (Ainda não foi salva) )
    return (notaAtual !== undefined && notaAtual !== null) &&
           (notaAtual !== notaOriginal || temArquivoNovo || notaOriginal === undefined);
  }

  // --- SALVAR UM ALUNO ---
  salvarNota(alunoId: number) {
    if (!this.disciplinaSelecionadaId) return;

    const payload = {
      aluno_id: alunoId,
      disciplina_id: this.disciplinaSelecionadaId,
      valor: this.notasTemporarias[alunoId],
      trimestre: this.trimestreSelecionado,
      descricao: 'Avaliação Contínua'
    };

    const arquivo = this.arquivosTemporarios[alunoId];

    this.notaService.lancarNota(payload, arquivo).subscribe({
      next: (res) => {
        // Atualiza a "Nota Original" para igualar a nova, desabilitando o botão
        this.notasOriginais[alunoId] = res.valor;
        if (res.arquivo_url) this.arquivosExistentes[alunoId] = res.arquivo_url;
        delete this.arquivosTemporarios[alunoId]; // Limpa o arquivo temporário da memória
        // Opcional: Mostrar um toast/notificação pequena em vez de alert
      },
      error: (err) => alert('Erro ao salvar.')
    });
  }

  // --- SALVAR TUDO (Bulk) ---
  salvarTudo() {
    if (!this.disciplinaSelecionadaId) return;

    // Filtra alunos que têm alterações pendentes
    const alunosParaSalvar = this.alunos.filter(a => this.podeSalvar(a.id!));

    if (alunosParaSalvar.length === 0) {
      alert("Não há alterações pendentes para salvar.");
      return;
    }

    this.loading = true;

    // Cria um array de Pedidos (Observables)
    const pedidos = alunosParaSalvar.map(aluno => {
      const payload = {
        aluno_id: aluno.id!,
        disciplina_id: this.disciplinaSelecionadaId!,
        valor: this.notasTemporarias[aluno.id!],
        trimestre: this.trimestreSelecionado,
        descricao: 'Avaliação Contínua'
      };
      const arquivo = this.arquivosTemporarios[aluno.id!];
      return this.notaService.lancarNota(payload, arquivo);
    });

    // forkJoin espera todos os pedidos terminarem
    forkJoin(pedidos).subscribe({
      next: (resultados) => {
        // Atualiza o estado local de todos
        resultados.forEach(res => {
          this.notasOriginais[res.aluno_id] = res.valor;
          if (res.arquivo_url) this.arquivosExistentes[res.aluno_id] = res.arquivo_url;
          delete this.arquivosTemporarios[res.aluno_id];
        });
        this.loading = false;
        alert(`${resultados.length} notas salvas com sucesso!`);
      },
      error: (err) => {
        console.error(err);
        this.loading = false;
        alert('Ocorreu um erro ao salvar algumas notas.');
      }
    });
  }

  // Função para abrir o arquivo numa nova aba
  verArquivo(caminhoRelativo: string) {
    // O caminho no banco já vem como "arquivos/nome-do-ficheiro.pdf"
    // Nós apenas adicionamos o endereço do servidor
    const urlCompleta = `http://127.0.0.1:8000/${caminhoRelativo}`;
    window.open(urlCompleta, '_blank');
  }
}
