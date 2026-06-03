from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.dose_log import DoseLog
from app.models.medication import Medication
from app.models.patient import Patient
from datetime import datetime, date, timedelta
import json

doses_bp = Blueprint("doses", __name__)


def owns_medication(med_id):
    uid = int(get_jwt_identity())
    med = db.session.get(Medication, med_id)
    if not med:
        return None
    patient = Patient.query.filter_by(id=med.patient_id, user_id=uid).first()
    return med if patient else None


@doses_bp.route("/today/<int:patient_id>", methods=["GET"])
@jwt_required()
def today_doses(patient_id):
    uid = int(get_jwt_identity())
    patient = Patient.query.filter_by(id=patient_id, user_id=uid).first_or_404()
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = today_start + timedelta(days=1)

    logs = (
        DoseLog.query
        .join(Medication)
        .filter(
            Medication.patient_id == patient_id,
            DoseLog.scheduled_time >= today_start,
            DoseLog.scheduled_time < today_end,
        )
        .order_by(DoseLog.scheduled_time)
        .all()
    )
    return jsonify([d.to_dict() for d in logs])


@doses_bp.route("/confirm/<int:log_id>", methods=["POST"])
@jwt_required()
def confirm_dose(log_id):
    log = db.session.get(DoseLog, log_id)
    if not log:
        return jsonify({"error": "Dose não encontrada"}), 404
    med = owns_medication(log.medication_id)
    if not med:
        return jsonify({"error": "Não autorizado"}), 403
    if log.status != "pending":
        return jsonify({"error": "Dose já foi confirmada ou marcada como perdida"}), 409
    log.status = "taken"
    log.taken_at = datetime.utcnow()
    if med.stock_quantity is not None and med.stock_quantity > 0:
        med.stock_quantity -= 1
    db.session.commit()
    return jsonify(log.to_dict())


@doses_bp.route("/skip/<int:log_id>", methods=["POST"])
@jwt_required()
def skip_dose(log_id):
    log = db.session.get(DoseLog, log_id)
    if not log:
        return jsonify({"error": "Dose não encontrada"}), 404
    if not owns_medication(log.medication_id):
        return jsonify({"error": "Não autorizado"}), 403
    if log.status != "pending":
        return jsonify({"error": "Dose já foi confirmada ou marcada como perdida"}), 409
    log.status = "missed"
    db.session.commit()
    return jsonify(log.to_dict())


@doses_bp.route("/history/<int:patient_id>", methods=["GET"])
@jwt_required()
def history(patient_id):
    uid = int(get_jwt_identity())
    Patient.query.filter_by(id=patient_id, user_id=uid).first_or_404()

    try:
        days = max(1, min(int(request.args.get("days", 30)), 365))
    except (ValueError, TypeError):
        days = 30

    since = datetime.utcnow() - timedelta(days=days)

    logs = (
        DoseLog.query
        .join(Medication)
        .filter(
            Medication.patient_id == patient_id,
            DoseLog.scheduled_time >= since,
        )
        .order_by(DoseLog.scheduled_time.desc())
        .all()
    )

    total = len(logs)
    taken = sum(1 for l in logs if l.status == "taken")
    missed = sum(1 for l in logs if l.status == "missed")
    adherence = round((taken / total * 100) if total > 0 else 0, 1)

    return jsonify({
        "logs": [d.to_dict() for d in logs],
        "summary": {
            "total": total,
            "taken": taken,
            "missed": missed,
            "pending": total - taken - missed,
            "adherence_percent": adherence,
        },
    })

