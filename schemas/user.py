from marshmallow import pre_dump

from ma import ma
from models.user import UserModel

# Note: Loading = Deserializing -> dict to object
#       Dumping = Serializing -> object to dict


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_only = ("password",)  # password field is only for loading, no returns
        dump_only = ("id", "activated")
        load_instance = True

    @pre_dump
    def _pre_dump(self, user: UserModel, **kwargs):
        user.confirmation = [user.most_recent_confirmation]
        return user
