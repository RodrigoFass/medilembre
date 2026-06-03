from app import db
from datetime import datetime
import json


class Medication(db.Model):
    __tablename__ = "medications"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    dose = db.Column(db.String(60), nullable=False)
    frequency = db.Column(db.String(60), nullable=False)
    # JSON string: ["08:00","14:00","20:00"]
    schedule_times = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    stock_quantity = db.Column(db.Integer, nullable=True)
    stock_alert_at = db.Column(db.Integer, default=5)
    instructions = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    dose_logs = db.relationship("DoseLog", backref="medication", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "name": self.name,
            "dose": self.dose,
            "frequency": self.frequency,
            "schedule_times": json.loads(self.schedule_times),
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "stock_quantity": self.stock_quantity,
            "stock_alert_at": self.stock_alert_at,
            "instructions": self.instructions,
            "active": self.active,
        }
