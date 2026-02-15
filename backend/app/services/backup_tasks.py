# backend/app/tasks/backup_tasks.py - TAREFAS AGENDADAS
from celery import Celery
from celery.schedules import crontab
from app.services.backup_service import BackupService
from app.core.config import settings

celery_app = Celery(
    'erp_escolar',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.beat_schedule = {
    # Backup diário às 02:00
    'daily-database-backup': {
        'task': 'app.tasks.backup_tasks.create_database_backup',
        'schedule': crontab(hour=2, minute=0),
    },
    # Backup de arquivos semanal (domingo 03:00)
    'weekly-files-backup': {
        'task': 'app.tasks.backup_tasks.create_files_backup',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),
    },
    # Backup completo mensal (dia 1, 04:00)
    'monthly-full-backup': {
        'task': 'app.tasks.backup_tasks.create_full_backup',
        'schedule': crontab(hour=4, minute=0, day_of_month=1),
    },
}

@celery_app.task
def create_database_backup():
    """Task de backup do banco de dados"""
    backup_service = BackupService()
    result = backup_service.create_database_backup()
    return {"status": "success", "backup_file": result}

@celery_app.task
def create_files_backup():
    """Task de backup de arquivos"""
    backup_service = BackupService()
    result = backup_service.create_files_backup()
    return {"status": "success", "backup_file": result}

@celery_app.task
def create_full_backup():
    """Task de backup completo"""
    backup_service = BackupService()
    result = backup_service.create_full_backup()
    return {"status": "success", "backups": result}