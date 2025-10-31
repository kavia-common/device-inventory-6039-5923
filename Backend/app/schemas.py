from marshmallow import Schema, fields, validate


class DeviceSchema(Schema):
    """Device schema for serialization/deserialization with all required fields."""
    name = fields.Str(required=True, description="Unique device name")
    ip_address = fields.IPv4(required=True, description="Device IP address")
    type = fields.Str(required=True, validate=validate.OneOf(["Router", "Switch", "Server"]), description="Device type")
    location = fields.Str(required=True, description="Device location")


class DeviceCreateSchema(DeviceSchema):
    """Schema for device creation. Same required fields as Device."""
    pass


class DeviceUpdateSchema(Schema):
    """Schema for device update, excludes name and requires other fields."""
    ip_address = fields.IPv4(required=True, description="Device IP address")
    type = fields.Str(required=True, validate=validate.OneOf(["Router", "Switch", "Server"]), description="Device type")
    location = fields.Str(required=True, description="Device location")
