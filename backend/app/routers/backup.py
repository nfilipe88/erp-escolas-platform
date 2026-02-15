# backend/app/routers/backup.py - ENDPOINTS DE BACKUP
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.backup_service import BackupService
from app.core.auth import get_current_user
from app.core.permissions import require_permission, ResourceEnum, ActionEnum
from app.models.usuario import Usuario

router = APIRouter(prefix="/backups", tags=["backups"])

@router.post("/database")
@require_permission(ResourceEnum.CONFIGURACOES, ActionEnum.UPDATE)
def create_database_backup_endpoint(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar backup do banco de dados (apenas superadmin)"""
    if current_user.role.name != "superadmin":
        raise HTTPException(403, "Apenas superadmin pode criar backups")
    
    backup_service = BackupService()
    
    # Executar em background
    background_tasks.add_task(backup_service.create_database_backup)
    
    return {"message": "Backup iniciado em background"}

@router.post("/files")
@require_permission(ResourceEnum.CONFIGURACOES, ActionEnum.UPDATE)
def create_files_backup_endpoint(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar backup dos arquivos"""
    if current_user.role.name != "superadmin":
        raise HTTPException(403, "Apenas superadmin pode criar backups")
    
    backup_service = BackupService()
    background_tasks.add_task(backup_service.create_files_backup)
    
    return {"message": "Backup de arquivos iniciado"}

@router.post("/full")
@require_permission(ResourceEnum.CONFIGURACOES, ActionEnum.UPDATE)
def create_full_backup_endpoint(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar backup completo"""
    if current_user.role.name != "superadmin":
        raise HTTPException(403, "Apenas superadmin pode criar backups")
    
    backup_service = BackupService()
    background_tasks.add_task(backup_service.create_full_backup)
    
    return {"message": "Backup completo iniciado"}

@router.get("/")
@require_permission(ResourceEnum.CONFIGURACOES, ActionEnum.READ)
def list_backups(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar backups disponíveis"""
    if current_user.role.name != "superadmin":
        raise HTTPException(403, "Apenas superadmin pode listar backups")
    
    backup_service = BackupService()
    backups = backup_service.list_backups()
    
    return {"backups": backups}

@router.post("/restore/database")
@require_permission(ResourceEnum.CONFIGURACOES, ActionEnum.UPDATE)
def restore_database_endpoint(
    backup_filename: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Restaurar backup do banco de dados"""
    if current_user.role.name != "superadmin":
        raise HTTPException(403, "Apenas superadmin pode restaurar backups")
    
    backup_service = BackupService()
    
    try:
        result = backup_service.restore_database_backup(backup_filename)
        return {"message": "Banco de dados restaurado com sucesso"}
    except Exception as e:
        raise HTTPException(500, f"Erro ao restaurar: {str(e)}")