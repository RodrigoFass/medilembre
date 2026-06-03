from app import db
from datetime import datetime


class DoseLog(db.Model):
    __tablename__ = "dose_logs"

    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey("medications.id"), nullable=False, index=True)
    scheduled_time = db.Column(db.DateTime, nullable=False, index=True)
    taken_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default="pending", index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "medication_id": self.medication_id,
            "medication_name": self.medication.name if self.medication else None,
            "dose": self.medication.dose if self.medication else None,
            "scheduled_time": self.scheduled_time.isoformat(),
            "taken_at": self.taken_at.isoformat() if self.taken_at else None,
            "status": self.status,
        }
