#!/bin/bash
# scripts/disaster_recovery.sh - SCRIPT DE RECUPERAÇÃO

set -e  # Parar em caso de erro

echo "============================================"
echo "ERP Escolar - Recuperação de Desastres"
echo "============================================"
echo ""

# Variáveis
BACKUP_DIR="/backups"
RESTORE_DIR="/tmp/restore"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/var/log/disaster_recovery_${TIMESTAMP}.log"

# Funções
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    log "ERROR: $1"
    exit 1
}

# 1. Verificar backups disponíveis
log "Verificando backups disponíveis..."
if [ ! -d "$BACKUP_DIR" ]; then
    error "Diretório de backups não encontrado: $BACKUP_DIR"
fi

LATEST_DB_BACKUP=$(ls -t $BACKUP_DIR/db_backup_*.sql.gz 2>/dev/null | head -1)
LATEST_FILES_BACKUP=$(ls -t $BACKUP_DIR/files_backup_*.tar.gz 2>/dev/null | head -1)

if [ -z "$LATEST_DB_BACKUP" ]; then
    error "Nenhum backup de banco de dados encontrado"
fi

log "Backup de BD encontrado: $LATEST_DB_BACKUP"
log "Backup de arquivos encontrado: $LATEST_FILES_BACKUP"

# 2. Confirmar restauração
echo ""
echo "⚠️  ATENÇÃO: Esta operação irá SUBSTITUIR todos os dados atuais!"
echo ""
echo "Backups a serem restaurados:"
echo "  - Database: $LATEST_DB_BACKUP"
echo "  - Files: $LATEST_FILES_BACKUP"
echo ""
read -p "Deseja continuar? (digite 'SIM' para confirmar): " confirmation

if [ "$confirmation" != "SIM" ]; then
    log "Recuperação cancelada pelo usuário"
    exit 0
fi

# 3. Parar serviços
log "Parando serviços..."
docker-compose down

# 4. Criar backup de segurança dos dados atuais
log "Criando backup de segurança dos dados atuais..."
SAFETY_BACKUP_DIR="/backups/safety_backup_${TIMESTAMP}"
mkdir -p "$SAFETY_BACKUP_DIR"

# Backup do banco atual
docker-compose up -d db
sleep 5
docker-compose exec -T db pg_dump -U postgres erp_escolar > "$SAFETY_BACKUP_DIR/current_db.sql" || true

# Backup dos arquivos atuais
if [ -d "uploads" ]; then
    tar -czf "$SAFETY_BACKUP_DIR/current_files.tar.gz" uploads/
fi

log "Backup de segurança criado em: $SAFETY_BACKUP_DIR"

# 5. Restaurar banco de dados
log "Restaurando banco de dados..."
mkdir -p "$RESTORE_DIR"
gunzip -c "$LATEST_DB_BACKUP" > "$RESTORE_DIR/restore.sql"

# Recriar banco
docker-compose exec -T db psql -U postgres -c "DROP DATABASE IF EXISTS erp_escolar;"
docker-compose exec -T db psql -U postgres -c "CREATE DATABASE erp_escolar;"

# Restaurar dados
docker-compose exec -T db psql -U postgres erp_escolar < "$RESTORE_DIR/restore.sql"

log "Banco de dados restaurado com sucesso"

# 6. Restaurar arquivos
if [ -n "$LATEST_FILES_BACKUP" ]; then
    log "Restaurando arquivos..."
    
    # Remover arquivos atuais
    rm -rf uploads/
    
    # Extrair backup
    tar -xzf "$LATEST_FILES_BACKUP"
    
    log "Arquivos restaurados com sucesso"
fi

# 7. Reiniciar serviços
log "Reiniciando serviços..."
docker-compose up -d

# Aguardar serviços iniciarem
log "Aguardando serviços iniciarem..."
sleep 10

# 8. Verificar saúde dos serviços
log "Verificando saúde dos serviços..."

# Verificar API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log "✓ API está respondendo"
else
    error "✗ API não está respondendo"
fi

# Verificar banco de dados
if docker-compose exec -T db psql -U postgres -d erp_escolar -c "SELECT 1" > /dev/null 2>&1; then
    log "✓ Banco de dados está acessível"
else
    error "✗ Banco de dados não está acessível"
fi

# 9. Executar testes de integridade
log "Executando testes de integridade..."

# Verificar tabelas principais
TABLES=("alunos" "turmas" "usuarios" "notas" "mensalidades")
for table in "${TABLES[@]}"; do
    COUNT=$(docker-compose exec -T db psql -U postgres -d erp_escolar -t -c "SELECT COUNT(*) FROM $table;")
    log "  - Tabela $table: $COUNT registros"
done

# 10. Limpar arquivos temporários
log "Limpando arquivos temporários..."
rm -rf "$RESTORE_DIR"

# 11. Relatório final
echo ""
echo "============================================"
echo "Recuperação Concluída com Sucesso!"
echo "============================================"
echo ""
log "RESUMO DA RECUPERAÇÃO:"
log "  - Backup de BD restaurado: $LATEST_DB_BACKUP"
log "  - Backup de arquivos restaurado: $LATEST_FILES_BACKUP"
log "  - Backup de segurança em: $SAFETY_BACKUP_DIR"
log "  - Log completo em: $LOG_FILE"
echo ""
echo "⚠️  IMPORTANTE:"
echo "1. Verifique se todos os serviços estão funcionando corretamente"
echo "2. Teste o login e funcionalidades principais"
echo "3. O backup de segurança dos dados anteriores está em: $SAFETY_BACKUP_DIR"
echo "4. Em caso de problemas, contate o administrador do sistema"
echo ""

log "Recuperação finalizada com sucesso"