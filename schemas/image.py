from marshmallow import Schema, fields
from werkzeug.datastructures import FileStorage


class FileStorageField(fields.Field):
    default_error_messages = {"invalid": "Image is not valid."}

    def _deserialize(self, value, attr, data, **kwargs) -> FileStorage:
        if value is not None:
            if not isinstance(value, FileStorage):
                self.fail("invalid")
            return value

        return None


class ImageSchema(Schema):
    image = FileStorageField(required=True)
