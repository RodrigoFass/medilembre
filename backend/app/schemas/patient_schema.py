from marshmallow import Schema, fields, validate, pre_load


class PatientSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    birth_date = fields.Date(required=False, allow_none=True, load_default=None)
    notes = fields.Str(required=False, allow_none=True, load_default=None,
                       validate=validate.Length(max=500))

    @pre_load
    def vazio_vira_none(self, data, **kwargs):
        # o front manda "" quando o campo de data fica em branco; "" nao e uma
        # data valida, entao converto pra None antes de validar
        if isinstance(data, dict) and data.get("birth_date") == "":
            data = {**data, "birth_date": None}
        return data
