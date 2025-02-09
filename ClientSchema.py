from marshmallow import Schema, fields, ValidationError

class ClientSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    age = fields.Int(required=True, validate=lambda x: x > 16)
    