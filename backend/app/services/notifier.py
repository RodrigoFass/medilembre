from flask_mail import Message
from app import mail
import logging

logger = logging.getLogger(__name__)


def send_dose_reminder(user, patient, medication, log):
    try:
        msg = Message(
            subject=f"MediLembre: hora do {medication.name}",
            recipients=[user.email],
            html=f"""
            <div style="font-family:Arial,sans-serif;max-width:500px;margin:auto">
              <h2 style="color:#E07B39">MediLembre</h2>
              <p>Olá, <strong>{user.name}</strong>!</p>
              <p>Está na hora de administrar o medicamento de <strong>{patient.name}</strong>:</p>
              <div style="background:#FFF3E0;padding:16px;border-radius:8px;margin:16px 0">
                <p style="margin:0;font-size:18px"><strong>{medication.name}</strong></p>
                <p style="margin:4px 0;color:#666">Dose: {medication.dose}</p>
                <p style="margin:4px 0;color:#666">Horário: {log.scheduled_time.strftime('%H:%M')}</p>
                {"<p style='margin:4px 0;color:#666'>Observações: " + medication.instructions + "</p>" if medication.instructions else ""}
              </div>
              <p style="color:#999;font-size:12px">MediLembre — Cuidando de quem você ama</p>
            </div>
            """,
        )
        mail.send(msg)
    except Exception as e:
        logger.warning(f"Falha ao enviar lembrete para {user.email}: {e}")


def send_stock_alert(user, patient, medication):
    try:
        msg = Message(
            subject=f"MediLembre: estoque baixo de {medication.name}",
            recipients=[user.email],
            html=f"""
            <div style="font-family:Arial,sans-serif;max-width:500px;margin:auto">
              <h2 style="color:#E07B39">MediLembre — Alerta de Estoque</h2>
              <p>O estoque de <strong>{medication.name}</strong> de {patient.name}
                 está baixo: apenas <strong>{medication.stock_quantity} unidade(s)</strong> restante(s).</p>
              <p>Providencie a reposição para não interromper o tratamento.</p>
            </div>
            """,
        )
        mail.send(msg)
    except Exception as e:
        logger.warning(f"Falha ao enviar alerta de estoque para {user.email}: {e}")
