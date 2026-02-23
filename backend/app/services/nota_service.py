# app/services/nota_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.nota import Nota
from app.models.aluno import Aluno
from app.models.disciplina import Disciplina
from app.models.turma import Turma
from app.models.usuario import Usuario
from app.schemas import schema_nota
from app.cruds import crud_nota
# Precisamos validar se o aluno existe
from app.cruds import crud_aluno

class NotaService:
    def __init__(self, db: Session):
        self.db = db

    def _validar_acesso_escola(self, usuario: Usuario, escola_id: int):
        """Helper interno para validar permissão de escola"""
        if usuario.perfil != "superadmin":
            if not usuario.escola_id or usuario.escola_id != escola_id:
                raise HTTPException(status_code=403, detail="Acesso negado a dados desta escola.")

    def lancar_nota(self, dados: schema_nota.NotaCreate, usuario_logado: Usuario) -> Nota:
        """
        Lança uma nota para um aluno.
        Regras:
        1. Aluno deve existir.
        2. Disciplina deve existir na escola.
        3. Usuário deve ter permissão na escola.
        4. (Futuro) Professor só lança na sua disciplina.
        """
        
        # 1. Buscar Aluno
        aluno = self.db.query(Aluno).filter(Aluno.id == dados.aluno_id).first()
        if not aluno:
            raise HTTPException(status_code=404, detail="Aluno não encontrado.")
        
        self._validar_acesso_escola(usuario_logado, aluno.escola_id)

        # 2. Validar Disciplina
        disciplina = self.db.query(Disciplina).filter(Disciplina.id == dados.disciplina_id).first()
        if not disciplina:
             raise HTTPException(status_code=404, detail="Disciplina não encontrada.")
             
        if disciplina.escola_id != aluno.escola_id:
            raise HTTPException(status_code=400, detail="Disciplina e Aluno são de escolas diferentes.")

        # 3. Verificar duplicidade (Evitar dois lançamentos iguais para o mesmo dia/tipo)
        # Ex: Não pode ter duas "Prova 1" do "1º Trimestre" para o mesmo aluno/disciplina
        nota_existente = self.db.query(Nota).filter(
            Nota.aluno_id == dados.aluno_id,
            Nota.disciplina_id == dados.disciplina_id,
            Nota.trimestre == dados.trimestre,
            Nota.tipo_avaliacao == dados.tipo_avaliacao
        ).first()

        if nota_existente:
             raise HTTPException(
                 status_code=400, 
                 detail=f"Já existe uma nota de '{dados.tipo_avaliacao}' para este aluno neste trimestre. Use a rota de atualização."
             )

        # 4. Criar Nota
        nova_nota = Nota(
            aluno_id=dados.aluno_id,
            disciplina_id=dados.disciplina_id,
            turma_id=aluno.turma_id, # Infeir da matrícula atual do aluno
            escola_id=aluno.escola_id,
            valor=dados.valor,
            trimestre=dados.trimestre,
            tipo_avaliacao=dados.tipo_avaliacao,
            descricao=dados.descricao,
            data_avaliacao=dados.data_avaliacao
        )
        self.db.add(nova_nota)
        self.db.commit()
        self.db.refresh(nova_nota)
        return nova_nota

    def atualizar_nota(self, nota_id: int, dados: schema_nota.NotaUpdate, usuario_logado: Usuario) -> Nota:
        nota = self.db.query(Nota).filter(Nota.id == nota_id).first()
        if not nota:
            raise HTTPException(status_code=404, detail="Nota não encontrada.")
            
        self._validar_acesso_escola(usuario_logado, nota.escola_id)
        
        # Atualizar campos
        if dados.valor is not None:
            nota.valor = dados.valor
        if dados.descricao is not None:
            nota.descricao = dados.descricao
            
        self.db.commit()
        self.db.refresh(nota)
        return nota

    def excluir_nota(self, nota_id: int, usuario_logado: Usuario):
        # Apenas Admin/Superadmin ou Professor Autor (se implementado)
        nota = self.db.query(Nota).filter(Nota.id == nota_id).first()
        if not nota:
            raise HTTPException(status_code=404, detail="Nota não encontrada.")
            
        self._validar_acesso_escola(usuario_logado, nota.escola_id)
        
        self.db.delete(nota)
        self.db.commit()

    def listar_notas_aluno(self, aluno_id: int, usuario_logado: Usuario) -> List[Nota]:
        """Lista histórico completo do aluno"""
        aluno = self.db.query(Aluno).filter(Aluno.id == aluno_id).first()
        if not aluno:
            raise HTTPException(status_code=404, detail="Aluno não encontrado.")
            
        self._validar_acesso_escola(usuario_logado, aluno.escola_id)
        
        return self.db.query(Nota).filter(Nota.aluno_id == aluno_id).all()

    def listar_pauta_turma(self, turma_id: int, disciplina_id: int, trimestre: str, usuario_logado: Usuario):
        """
        Retorna as notas de todos os alunos de uma turma numa disciplina específica.
        Usado para a visão do Professor (Pauta).
        """
        turma = self.db.query(Turma).filter(Turma.id == turma_id).first()
        if not turma:
             raise HTTPException(status_code=404, detail="Turma não encontrada.")
        
        self._validar_acesso_escola(usuario_logado, turma.escola_id)
        
        # Buscar notas filtradas
        notas = self.db.query(Nota).filter(
            Nota.turma_id == turma_id,
            Nota.disciplina_id == disciplina_id,
            Nota.trimestre == trimestre
        ).all()
        
        return notas

    def calcular_medias_aluno(self, aluno_id: int, usuario_logado: Usuario):
        """
        Gera o Boletim em tempo real.
        Nota: Em sistemas grandes, isto seria calculado e cacheado/salvo no banco.
        Aqui calculamos on-the-fly para simplicidade.
        """
        notas = self.listar_notas_aluno(aluno_id, usuario_logado)
        
        # Agrupar por disciplina e trimestre
        # Estrutura: { 'Matemática': { '1º Trimestre': [12, 14], '2º Trimestre': [15] } }
        dados = {}
        
        for nota in notas:
            disc_nome = nota.disciplina.nome if nota.disciplina else f"Disc {nota.disciplina_id}"
            
            if disc_nome not in dados:
                dados[disc_nome] = {}
            
            if nota.trimestre not in dados[disc_nome]:
                dados[disc_nome][nota.trimestre] = []
                
            dados[disc_nome][nota.trimestre].append(nota.valor)
            
        # Calcular médias
        boletim = []
        for disciplina, trimestres in dados.items():
            t1 = trimestres.get("1º Trimestre", [])
            t2 = trimestres.get("2º Trimestre", [])
            t3 = trimestres.get("3º Trimestre", [])
            
            # Média simples das notas do trimestre (pode ser ponderada se quiser mudar a lógica)
            m1 = sum(t1)/len(t1) if t1 else None
            m2 = sum(t2)/len(t2) if t2 else None
            m3 = sum(t3)/len(t3) if t3 else None
            
            # Média Final (Exemplo simples)
            notas_finais = [m for m in [m1, m2, m3] if m is not None]
            media_final = sum(notas_finais)/len(notas_finais) if notas_finais else None
            
            resultado = "Em Curso"
            if media_final:
                resultado = "Aprovado" if media_final >= 10 else "Reprovado"

            boletim.append({
                "disciplina": disciplina,
                "nota_t1": round(m1, 1) if m1 else None,
                "nota_t2": round(m2, 1) if m2 else None,
                "nota_t3": round(m3, 1) if m3 else None,
                "media_final": round(media_final, 1) if media_final else None,
                "resultado": resultado
            })
            
        return boletim