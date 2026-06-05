from app import scheduler, db
from app.models.medication import Medication
from app.models.dose_log import DoseLog
from app.services.notifier import send_dose_reminder, send_stock_alert
from datetime import datetime, date, timedelta
from sqlalchemy.orm import joinedload
import json
import logging

logger = logging.getLogger(__name__)

# todas as datas são salvas e comparadas no horário local (America/Sao_Paulo)
# o scheduler também roda nesse fuso, então datetime.now() bate certinho


def generate_todays_logs(app):
    with app.app_context():
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())

        meds = (
            Medication.query
            .filter_by(active=True)
            .options(joinedload(Medication.dose_logs))
            .all()
        )

        new_logs = []
        for med in meds:
            if med.start_date > today:
                continue
            if med.end_date and med.end_date < today:
                continue

            existing_times = {
                log.scheduled_time
                for log in med.dose_logs
                if log.scheduled_time >= today_start
                and log.scheduled_time < today_start + timedelta(days=1)
            }

            times = json.loads(med.schedule_times)
            for t in times:
                h, m = map(int, t.split(":"))
                scheduled = today_start.replace(hour=h, minute=m)
                if scheduled not in existing_times:
                    new_logs.append(DoseLog(
                        medication_id=med.id,
                        scheduled_time=scheduled,
                        status="pending",
                    ))

        if new_logs:
            db.session.add_all(new_logs)
            db.session.commit()
        logger.info("Doses do dia geradas: %d novos registros", len(new_logs))


def mark_missed_doses(app):
    with app.app_context():
        # usa horário local pra bater com as datas salvas no banco
        cutoff = datetime.now() - timedelta(hours=1)
        overdue = DoseLog.query.filter(
            DoseLog.status == "pending",
            DoseLog.scheduled_time < cutoff,
        ).all()
        for log in overdue:
            log.status = "missed"
        if overdue:
            db.session.commit()


def check_reminders(app):
    with app.app_context():
        # usa horário local pra bater com as datas salvas no banco
        now = datetime.now()
        window_end = now + timedelta(minutes=5)

        upcoming = (
            DoseLog.query
            .filter(
                DoseLog.status == "pending",
                DoseLog.scheduled_time >= now,
                DoseLog.scheduled_time < window_end,
            )
            .options(
                joinedload(DoseLog.medication)
                .joinedload(Medication.patient)
            )
            .all()
        )

        for log in upcoming:
            med = log.medication
            patient = med.patient
            user = patient.user
            send_dose_reminder(user, patient, med, log)

            if med.stock_quantity is not None and med.stock_quantity <= med.stock_alert_at:
                send_stock_alert(user, patient, med)


def start_scheduler(app):
    if scheduler.running:
        return

    # não inicia o scheduler quando tá rodando os testes
    if app.config.get("TESTING"):
        return

    scheduler.add_job(
        generate_todays_logs,
        "cron",
        hour=0,
        minute=1,
        args=[app],
        id="generate_daily_logs",
        replace_existing=True,
    )
    scheduler.add_job(
        mark_missed_doses,
        "interval",
        minutes=30,
        args=[app],
        id="mark_missed",
        replace_existing=True,
    )
    scheduler.add_job(
        check_reminders,
        "interval",
        minutes=5,
        args=[app],
        id="check_reminders",
        replace_existing=True,
    )

    generate_todays_logs(app)
    scheduler.start()
    logger.info("Scheduler iniciado")
