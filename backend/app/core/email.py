import os
from typing import List
from pathlib import Path
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import SecretStr, EmailStr, BaseModel

# Carregar variáveis de ambiente
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Função auxiliar para garantir que não é None
def get_env(key: str, default: str = "") -> str:
    return os.getenv(key) or default

# Configurações do Servidor SMTP
# (Idealmente, coloca estes valores no teu ficheiro .env)
conf = ConnectionConfig(
    MAIL_USERNAME = get_env("MAIL_USERNAME"),
    MAIL_PASSWORD = get_env("MAIL_PASSWORD"), # A lib converte auto para SecretStr, ou podes usar SecretStr(get_env(..))
    MAIL_FROM = get_env("MAIL_FROM"),
    MAIL_PORT = int(get_env("MAIL_PORT", "587")),
    MAIL_SERVER = get_env("MAIL_SERVER"),
    MAIL_FROM_NAME = get_env("MAIL_FROM_NAME"),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

class EmailSchema(BaseModel):
    email: List[EmailStr]

async def send_reset_password_email(email: str, token: str):
    link = f"http://localhost:4200/reset-senha?token={token}"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 8px; padding: 20px;">
                <h2 style="color: #1e3a8a;">Recuperação de Senha 🔐</h2>
                <p>Olá,</p>
                <p>Recebemos um pedido para recuperar a senha da tua conta no <strong>ERP Escolar</strong>.</p>
                <p>Clica no botão abaixo para definir uma nova senha:</p>
                
                <a href="{link}" style="background-color: #1e3a8a; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0;">
                    Redefinir Minha Senha
                </a>
                
                <p style="font-size: 12px; color: #777;">Se não pediste isto, podes ignorar este email. O link expira em 15 minutos.</p>
            </div>
        </body>
    </html>
    """

    message = MessageSchema(
        subject="ERP Escolar - Recuperação de Senha",
        recipients=[email], # type: ignore (Pylance pode reclamar de List[str] vs List[EmailStr], mas funciona)
        body=html_content,
        subtype=MessageType.html # CORREÇÃO IMPORTANTE: Usar Enum
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)
    
async def enviar_email_recibo(destinatario: str, aluno_nome: str, valor: float, mes: str):
    """
    Envia um email formatado de recibo de pagamento.
    """
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px; max-width: 600px;">
        <h2 style="color: #4338ca;">Comprovativo de Pagamento 🎓</h2>
        <p>Prezado(a) Encarregado(a),</p>
        <p>Confirmamos a receção do pagamento referente ao aluno <strong>{aluno_nome}</strong>.</p>
        
        <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p><strong>Descrição:</strong> {mes}</p>
            <p><strong>Valor Pago:</strong> {valor:,.2f} Kz</p>
            <p><strong>Data:</strong> Hoje</p>
            <p><strong>Estado:</strong> <span style="color: green; font-weight: bold;">CONFIRMADO</span></p>
        </div>

        <p style="font-size: 12px; color: #6b7280;">Este é um email automático. Por favor, não responda.</p>
        <p>Cumprimentos,<br><strong>A Direção da Escola</strong></p>
    </div>
    """

    message = MessageSchema(
        subject=f"Recibo de Pagamento - {aluno_nome}",
        recipients=[destinatario],
        body=html_content,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    
    try:
        await fm.send_message(message)
        print(f"📧 Email enviado com sucesso para {destinatario}")
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")