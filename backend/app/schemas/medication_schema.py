from marshmallow import Schema, fields, validate, validates, ValidationError
import re


class MedicationSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    dose = fields.Str(required=True, validate=validate.Length(min=1, max=60))
    frequency = fields.Str(required=True, validate=validate.Length(min=1, max=60))
    schedule_times = fields.List(fields.Str(), required=True,
                                 validate=validate.Length(min=1))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=False, allow_none=True, load_default=None)
    stock_quantity = fields.Int(required=False, allow_none=True, load_default=None,
                                validate=validate.Range(min=0))
    stock_alert_at = fields.Int(required=False, load_default=5,
                                validate=validate.Range(min=0))
    instructions = fields.Str(required=False, allow_none=True, load_default=None)

    @validates("schedule_times")
    def validate_times(self, value):
        pattern = re.compile(r"^\d{2}:\d{2}$")
        for t in value:
            if not pattern.match(t):
                raise ValidationError(f"Horário inválido: '{t}'. Use o formato HH:MM.")
