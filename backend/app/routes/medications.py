from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app import db
from app.models.medication import Medication
from app.models.patient import Patient
from app.schemas import MedicationSchema
import json

medications_bp = Blueprint("medications", __name__)
medication_schema = MedicationSchema()


def owns_patient(patient_id):
    uid = int(get_jwt_identity())
    return Patient.query.filter_by(id=patient_id, user_id=uid).first()


@medications_bp.route("/patient/<int:pid>", methods=["GET"])
@jwt_required()
def list_medications(pid):
    if not owns_patient(pid):
        return jsonify({"error": "Não autorizado"}), 403
    meds = Medication.query.filter_by(patient_id=pid).all()
    return jsonify([m.to_dict() for m in meds])


@medications_bp.route("/patient/<int:pid>", methods=["POST"])
@jwt_required()
def create_medication(pid):
    if not owns_patient(pid):
        return jsonify({"error": "Não autorizado"}), 403
    try:
        data = medication_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "Dados inválidos", "messages": e.messages}), 422

    med = Medication(
        patient_id=pid,
        name=data["name"],
        dose=data["dose"],
        frequency=data["frequency"],
        schedule_times=json.dumps(data["schedule_times"]),
        start_date=data["start_date"],
        end_date=data.get("end_date"),
        stock_quantity=data.get("stock_quantity"),
        stock_alert_at=data.get("stock_alert_at", 5),
        instructions=data.get("instructions"),
    )
    db.session.add(med)
    db.session.commit()
    return jsonify(med.to_dict()), 201


@medications_bp.route("/<int:mid>", methods=["PUT"])
@jwt_required()
def update_medication(mid):
    med = db.session.get(Medication, mid)
    if not med:
        return jsonify({"error": "Medicamento não encontrado"}), 404
    if not owns_patient(med.patient_id):
        return jsonify({"error": "Não autorizado"}), 403
    try:
        data = medication_schema.load(request.get_json() or {}, partial=True)
    except ValidationError as e:
        return jsonify({"error": "Dados inválidos", "messages": e.messages}), 422

    for field in ["name", "dose", "frequency", "instructions"]:
        if field in data:
            setattr(med, field, data[field])
    if "schedule_times" in data:
        med.schedule_times = json.dumps(data["schedule_times"])
    if "start_date" in data:
        med.start_date = data["start_date"]
    if "end_date" in data:
        med.end_date = data["end_date"]
    if "stock_quantity" in data:
        med.stock_quantity = data["stock_quantity"]
    if "stock_alert_at" in data:
        med.stock_alert_at = data["stock_alert_at"]
    if "active" in data:
        med.active = data["active"]
    db.session.commit()
    return jsonify(med.to_dict())


@medications_bp.route("/<int:mid>", methods=["DELETE"])
@jwt_required()
def delete_medication(mid):
    med = db.session.get(Medication, mid)
    if not med:
        return jsonify({"error": "Medicamento não encontrado"}), 404
    if not owns_patient(med.patient_id):
        return jsonify({"error": "Não autorizado"}), 403
    db.session.delete(med)
    db.session.commit()
    return jsonify({"ok": True})
