# app/services/financeiro_service.py
from typing import List
from datetime import date, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.mensalidade import Mensalidade
from app.models.aluno import Aluno
from app.models.usuario import Usuario
from app.schemas import schema_mensalidade

class FinanceiroService:
    def __init__(self, db: Session):
        self.db = db

    def _verificar_permissao(self, usuario: Usuario, escola_id: int):
        """Apenas Admin, Superadmin ou Financeiro podem mexer aqui"""
        if usuario.perfil == "superadmin":
            return
        
        if usuario.perfil not in ["admin", "financeiro"]:
            raise HTTPException(status_code=403, detail="Sem permissão para operações financeiras.")
            
        if usuario.escola_id != escola_id:
            raise HTTPException(status_code=403, detail="Acesso negado a dados financeiros de outra escola.")

    def gerar_carnet_anual(self, dados: schema_mensalidade.GerarCarnetRequest, usuario_logado: Usuario) -> List[Mensalidade]:
        """
        Gera mensalidades de Fevereiro a Dezembro (exemplo escolar) para um aluno.
        Evita duplicatas se o mês já existir.
        """
        aluno = self.db.query(Aluno).filter(Aluno.id == dados.aluno_id).first()
        if not aluno:
            raise HTTPException(status_code=404, detail="Aluno não encontrado.")
            
        self._verificar_permissao(usuario_logado, aluno.escola_id)

        mensalidades_criadas = []
        
        # Exemplo: Ano letivo escolar (ajuste conforme a realidade do país, aqui pus 1 a 12)
        meses = range(1, 13) 

        for mes in meses:
            # Verifica se já existe
            existe = self.db.query(Mensalidade).filter(
                Mensalidade.aluno_id == aluno.id,
                Mensalidade.mes == mes,
                Mensalidade.ano == dados.ano_letivo
            ).first()

            if not existe:
                # Lógica para data de vencimento (Cuidado com fevereiro/dias 31)
                try:
                    vencimento = date(dados.ano_letivo, mes, dados.dia_vencimento)
                except ValueError:
                    # Fallback para o último dia do mês se dia 30/31 falhar
                    if mes == 12:
                         vencimento = date(dados.ano_letivo, 12, 31)
                    else:
                         vencimento = date(dados.ano_letivo, mes + 1, 1) - timedelta(days=1)

                nova = Mensalidade(
                    aluno_id=aluno.id,
                    escola_id=aluno.escola_id,
                    mes=mes,
                    ano=dados.ano_letivo,
                    valor=dados.valor_mensal,
                    data_vencimento=vencimento,
                    status="Pendente"
                )
                self.db.add(nova)
                mensalidades_criadas.append(nova)
        
        self.db.commit()
        return mensalidades_criadas

    def registrar_pagamento(self, mensalidade_id: int, dados: schema_mensalidade.RealizarPagamento, usuario_logado: Usuario) -> Mensalidade:
        """
        Baixa de pagamento.
        Bloqueia se já estiver pago.
        """
        mensalidade = self.db.query(Mensalidade).filter(Mensalidade.id == mensalidade_id).first()
        if not mensalidade:
            raise HTTPException(status_code=404, detail="Mensalidade não encontrada.")
            
        self._verificar_permissao(usuario_logado, mensalidade.escola_id)

        if mensalidade.status == "Pago":
            raise HTTPException(status_code=400, detail="Esta mensalidade já foi paga.")

        # Atualiza dados
        mensalidade.status = "Pago"
        mensalidade.data_pagamento = date.today()
        mensalidade.forma_pagamento = dados.forma_pagamento
        mensalidade.observacao = dados.observacao
        
        # Valor final = Valor Original + Multa - Desconto
        valor_final = mensalidade.valor + dados.multa - dados.desconto
        mensalidade.valor_pago = valor_final # Assumindo que existe este campo no model

        self.db.commit()
        self.db.refresh(mensalidade)
        return mensalidade

    def cancelar_mensalidade(self, mensalidade_id: int, motivo: str, usuario_logado: Usuario):
        """Cancela uma cobrança (ex: aluno saiu da escola)"""
        mensalidade = self.db.query(Mensalidade).filter(Mensalidade.id == mensalidade_id).first()
        if not mensalidade:
            raise HTTPException(status_code=404, detail="Mensalidade não encontrada.")
            
        self._verificar_permissao(usuario_logado, mensalidade.escola_id)
        
        if mensalidade.status == "Pago":
            raise HTTPException(status_code=400, detail="Não pode cancelar uma mensalidade já paga. Faça o estorno primeiro.")

        mensalidade.status = "Cancelado"
        mensalidade.observacao = f"Cancelado por {usuario_logado.nome}: {motivo}"
        self.db.commit()

    def listar_por_aluno(self, aluno_id: int, usuario_logado: Usuario) -> List[Mensalidade]:
        aluno = self.db.query(Aluno).filter(Aluno.id == aluno_id).first()
        if not aluno:
             raise HTTPException(status_code=404, detail="Aluno não encontrado.")
             
        self._verificar_permissao(usuario_logado, aluno.escola_id)
        
        # Verifica atrasos automaticamente (regra simples)
        mensalidades = self.db.query(Mensalidade).filter(Mensalidade.aluno_id == aluno_id).order_by(Mensalidade.mes).all()
        
        hoje = date.today()
        for m in mensalidades:
            if m.status == "Pendente" and m.data_vencimento < hoje:
                m.status = "Atrasado"
                # Nota: Aqui não fazemos commit para não "sujar" o banco em query de leitura, 
                # mas o ideal seria um Job noturno que atualiza status.
        
        return mensalidades