# backend/app/services/backup_service.py - NOVO ARQUIVO
import os
import subprocess
import boto3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import shutil
import tarfile
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class BackupService:
    """Serviço de backup e recuperação"""
    
    def __init__(self):
        self.backup_dir = Path("/backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configurar S3 se disponível
        if settings.AWS_ACCESS_KEY_ID:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.s3_bucket = settings.BACKUP_S3_BUCKET
        else:
            self.s3_client = None
    
    def create_database_backup(self) -> str:
        """Criar backup do banco de dados"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"db_backup_{timestamp}.sql"
            backup_path = self.backup_dir / backup_filename
            
            logger.info(f"Iniciando backup do banco de dados: {backup_filename}")
            
            # Executar pg_dump
            cmd = [
                "pg_dump",
                "-h", settings.DATABASE_HOST,
                "-U", settings.DATABASE_USER,
                "-d", settings.DATABASE_NAME,
                "-F", "c",  # Custom format (compressed)
                "-f", str(backup_path)
            ]
            
            env = os.environ.copy()
            env["PGPASSWORD"] = settings.DATABASE_PASSWORD
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"pg_dump falhou: {result.stderr}")
            
            logger.info(f"Backup criado com sucesso: {backup_path}")
            
            # Comprimir
            compressed_path = self._compress_backup(backup_path)
            
            # Upload para S3
            if self.s3_client:
                self._upload_to_s3(compressed_path)
            
            # Limpar backups antigos
            self._cleanup_old_backups()
            
            return str(compressed_path)
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {str(e)}")
            raise
    
    def create_files_backup(self) -> str:
        """Backup dos arquivos uploadados"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"files_backup_{timestamp}.tar.gz"
            backup_path = self.backup_dir / backup_filename
            
            logger.info(f"Iniciando backup de arquivos: {backup_filename}")
            
            # Criar arquivo tar
            uploads_dir = Path("uploads")
            if not uploads_dir.exists():
                logger.warning("Diretório de uploads não existe")
                return ""
            
            with tarfile.open(backup_path, "w:gz") as tar:
                tar.add(uploads_dir, arcname="uploads")
            
            logger.info(f"Backup de arquivos criado: {backup_path}")
            
            # Upload para S3
            if self.s3_client:
                self._upload_to_s3(backup_path)
            
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Erro ao criar backup de arquivos: {str(e)}")
            raise
    
    def create_full_backup(self) -> dict:
        """Criar backup completo (banco + arquivos)"""
        try:
            db_backup = self.create_database_backup()
            files_backup = self.create_files_backup()
            
            return {
                "database": db_backup,
                "files": files_backup,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao criar backup completo: {str(e)}")
            raise
    
    def restore_database_backup(self, backup_file: str) -> bool:
        """Restaurar backup do banco de dados"""
        try:
            backup_path = Path(backup_file)
            
            if not backup_path.exists():
                raise FileNotFoundError(f"Arquivo de backup não encontrado: {backup_file}")
            
            logger.warning(f"RESTAURANDO BACKUP: {backup_file}")
            
            # Descomprimir se necessário
            if backup_path.suffix == ".gz":
                backup_path = self._decompress_backup(backup_path)
            
            # Executar pg_restore
            cmd = [
                "pg_restore",
                "-h", settings.DATABASE_HOST,
                "-U", settings.DATABASE_USER,
                "-d", settings.DATABASE_NAME,
                "--clean",  # Limpar antes de restaurar
                "--if-exists",
                str(backup_path)
            ]
            
            env = os.environ.copy()
            env["PGPASSWORD"] = settings.DATABASE_PASSWORD
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"pg_restore falhou: {result.stderr}")
            
            logger.info("Banco de dados restaurado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {str(e)}")
            raise
    
    def restore_files_backup(self, backup_file: str) -> bool:
        """Restaurar backup de arquivos"""
        try:
            backup_path = Path(backup_file)
            
            if not backup_path.exists():
                raise FileNotFoundError(f"Arquivo de backup não encontrado: {backup_file}")
            
            logger.warning(f"RESTAURANDO ARQUIVOS: {backup_file}")
            
            # Extrair tar
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(path=".")
            
            logger.info("Arquivos restaurados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar arquivos: {str(e)}")
            raise
    
    def list_backups(self) -> list:
        """Listar backups disponíveis"""
        backups = []
        
        # Backups locais
        for backup_file in self.backup_dir.glob("*.sql*"):
            backups.append({
                "filename": backup_file.name,
                "path": str(backup_file),
                "size": backup_file.stat().st_size,
                "created": datetime.fromtimestamp(backup_file.stat().st_mtime),
                "location": "local"
            })
        
        # Backups no S3
        if self.s3_client:
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.s3_bucket,
                    Prefix="backups/"
                )
                
                for obj in response.get('Contents', []):
                    backups.append({
                        "filename": obj['Key'].split('/')[-1],
                        "path": obj['Key'],
                        "size": obj['Size'],
                        "created": obj['LastModified'],
                        "location": "s3"
                    })
            except Exception as e:
                logger.error(f"Erro ao listar backups S3: {str(e)}")
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def _compress_backup(self, file_path: Path) -> Path:
        """Comprimir arquivo de backup"""
        compressed_path = file_path.with_suffix(file_path.suffix + ".gz")
        
        with open(file_path, 'rb') as f_in:
            with tarfile.open(compressed_path, 'w:gz') as tar:
                tarinfo = tarfile.TarInfo(name=file_path.name)
                tarinfo.size = file_path.stat().st_size
                tar.addfile(tarinfo, f_in)
        
        # Remover arquivo original
        file_path.unlink()
        
        return compressed_path
    
    def _decompress_backup(self, file_path: Path) -> Path:
        """Descomprimir arquivo de backup"""
        decompressed_path = file_path.with_suffix('')
        
        with tarfile.open(file_path, 'r:gz') as tar:
            tar.extractall(path=file_path.parent)
        
        return decompressed_path
    
    def _upload_to_s3(self, file_path: Path) -> bool:
        """Fazer upload do backup para S3"""
        try:
            s3_key = f"backups/{file_path.name}"
            
            self.s3_client.upload_file(
                str(file_path),
                self.s3_bucket,
                s3_key
            )
            
            logger.info(f"Backup enviado para S3: {s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar backup para S3: {str(e)}")
            return False
    
    def _cleanup_old_backups(self, days: int = 30):
        """Remover backups antigos"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Limpar backups locais
            for backup_file in self.backup_dir.glob("*.sql*"):
                file_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_date < cutoff_date:
                    backup_file.unlink()
                    logger.info(f"Backup antigo removido: {backup_file.name}")
            
            # Limpar backups S3
            if self.s3_client:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.s3_bucket,
                    Prefix="backups/"
                )
                
                for obj in response.get('Contents', []):
                    if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                        self.s3_client.delete_object(
                            Bucket=self.s3_bucket,
                            Key=obj['Key']
                        )
                        logger.info(f"Backup S3 antigo removido: {obj['Key']}")
                        
        except Exception as e:
            logger.error(f"Erro ao limpar backups antigos: {str(e)}")