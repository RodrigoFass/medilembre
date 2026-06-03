from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app import db
from app.models.patient import Patient
from app.schemas import PatientSchema

patients_bp = Blueprint("patients", __name__)
patient_schema = PatientSchema()


def current_user_id():
    return int(get_jwt_identity())


@patients_bp.route("/", methods=["GET"])
@jwt_required()
def list_patients():
    patients = Patient.query.filter_by(user_id=current_user_id()).all()
    return jsonify([p.to_dict() for p in patients])


@patients_bp.route("/<int:pid>", methods=["GET"])
@jwt_required()
def get_patient(pid):
    patient = Patient.query.filter_by(id=pid, user_id=current_user_id()).first_or_404()
    return jsonify(patient.to_dict())


@patients_bp.route("/", methods=["POST"])
@jwt_required()
def create_patient():
    try:
        data = patient_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "Dados inválidos", "messages": e.messages}), 422

    patient = Patient(
        user_id=current_user_id(),
        name=data["name"],
        birth_date=data.get("birth_date"),
        notes=data.get("notes"),
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify(patient.to_dict()), 201


@patients_bp.route("/<int:pid>", methods=["PUT"])
@jwt_required()
def update_patient(pid):
    patient = Patient.query.filter_by(id=pid, user_id=current_user_id()).first_or_404()
    try:
        data = patient_schema.load(request.get_json() or {}, partial=True)
    except ValidationError as e:
        return jsonify({"error": "Dados inválidos", "messages": e.messages}), 422

    if "name" in data:
        patient.name = data["name"]
    if "notes" in data:
        patient.notes = data["notes"]
    if "birth_date" in data:
        patient.birth_date = data["birth_date"]
    db.session.commit()
    return jsonify(patient.to_dict())


@patients_bp.route("/<int:pid>", methods=["DELETE"])
@jwt_required()
def delete_patient(pid):
    patient = Patient.query.filter_by(id=pid, user_id=current_user_id()).first_or_404()
    db.session.delete(patient)
    db.session.commit()
    return jsonify({"ok": True})
