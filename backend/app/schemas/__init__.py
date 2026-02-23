from .schema_aluno import AlunoCreate, AlunoResponse
from .schema_boletim import BoletimResponse, LinhaBoletim, NotaBoletim
from .schema_configuracao import ConfiguracaoUpdate, ConfiguracaoResponse
from .schema_dashboard import DashboardStats
from .schema_diario import DiarioResponse, DiarioCreate
from .schema_disciplina import DisciplinaCreate, DisciplinaResponse
from .schema_escola import EscolaCreate, EscolaResponse
from .schema_horario import HorarioCreate, HorarioResponse, HorarioUpdate
from .schema_mensalidade import MensalidadeCreate, MensalidadePagar, MensalidadeResponse
from .schema_nota import NotaCreate, NotaResponse
from .schema_presenca import PresencaItem, ChamadaDiaria, PresencaResponse
from .schema_turma import TurmaCreate, TurmaResponse
from .schema_usuario import UsuarioCreate, UsuarioResponse, Token
from .schema_atribuicao import AtribuicaoCreate, AtribuicaoResponse
from .schema_notificacao import NotificacaoCreate, NotificacaoResponse
from .schema_relatorio import ResumoFinanceiro, TransacaoFinanceira, Devedor