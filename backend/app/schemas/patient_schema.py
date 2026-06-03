from marshmallow import Schema, fields, validate


class PatientSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    birth_date = fields.Date(required=False, allow_none=True, load_default=None)
    notes = fields.Str(required=False, allow_none=True, load_default=None,
                       validate=validate.Length(max=500))
