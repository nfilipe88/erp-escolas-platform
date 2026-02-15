# backend/app/core/file_handler.py - NOVO ARQUIVO
from fastapi import UploadFile, HTTPException
from pathlib import Path
import magic  # python-magic
import hashlib
from typing import Optional

class SecureFileHandler:
    """Handler seguro para upload de arquivos"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'image/jpeg',
        'image/png',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR = Path("uploads")
    
    @classmethod
    async def validate_and_save(
        cls,
        file: UploadFile,
        subfolder: str = "documentos"
    ) -> dict:
        """Validar e salvar arquivo com segurança"""
        
        # 1. Verificar se arquivo foi enviado
        if not file or not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Nenhum arquivo enviado"
            )
        
        # 2. Validar extensão
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Extensão não permitida. Permitidas: {cls.ALLOWED_EXTENSIONS}"
            )
        
        # 3. Ler conteúdo
        content = await file.read()
        
        # 4. Verificar tamanho
        if len(content) > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo muito grande. Máximo: {cls.MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # 5. Verificar MIME type real (não confiar na extensão)
        mime_type = magic.from_buffer(content, mime=True)
        if mime_type not in cls.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de arquivo não permitido: {mime_type}"
            )
        
        # 6. Gerar nome seguro
        file_hash = hashlib.sha256(content).hexdigest()[:16]
        safe_filename = f"{file_hash}{file_ext}"
        
        # 7. Criar diretório se não existir
        upload_path = cls.UPLOAD_DIR / subfolder
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # 8. Salvar arquivo
        file_path = upload_path / safe_filename
        
        # Evitar sobrescrever
        counter = 1
        while file_path.exists():
            safe_filename = f"{file_hash}_{counter}{file_ext}"
            file_path = upload_path / safe_filename
            counter += 1
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 9. Retornar informações
        return {
            "filename": safe_filename,
            "path": str(file_path.relative_to(cls.UPLOAD_DIR)),
            "size": len(content),
            "mime_type": mime_type,
            "url": f"/arquivos/{subfolder}/{safe_filename}"
        }
    
    @classmethod
    def delete_file(cls, file_path: str) -> bool:
        """Deletar arquivo com segurança"""
        try:
            full_path = cls.UPLOAD_DIR / file_path
            
            # Verificar path traversal
            if not str(full_path.resolve()).startswith(str(cls.UPLOAD_DIR.resolve())):
                raise HTTPException(status_code=400, detail="Caminho inválido")
            
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao deletar arquivo: {str(e)}")
