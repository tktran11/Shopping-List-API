import traceback

from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)

from models.user import UserModel
from models.confirmation import ConfirmationModel
from libs.mailgun import MailGunException
from libs.strings import gettext
from schemas.user import UserSchema
from blacklist import BLACKLIST

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user = user_schema.load(user_json)

        if UserModel.find_by_username(user.username):
            return {"message": gettext("user_name_already_exists")}, 400

        if UserModel.find_by_email(user.email):
            return {"message": gettext("user_email_already_exists")}, 400

        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": gettext("user_creation_success")}, 201

        except MailGunException as error:
            user.delete_from_db()
            return {"message": str(error)}, 500

        except:  # failed to save user to db
            traceback.print_exc()
            user.delete_from_db()
            return {"message": gettext("user_creation_failure")}, 500


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_found")}, 404

        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_found")}, 404

        user.delete_from_db()
        return {"message": gettext("user_deleted")}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        # Have marshmallow ignore email loading if email is missing here
        user_data = user_schema.load(user_json, partial=("email",))

        user = UserModel.find_by_username(user_data.username)

        if user and user_data.password == user.password:
            confirmation = user.most_recent_confirmation
            if confirmation and confirmation.is_confirmed:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return (
                    {"access_token": access_token, "refresh_token": refresh_token},
                    200,
                )
            return (
                {"message": gettext("user_not_confirmed_error").format(user.email)},
                400,
            )

        return {"message": gettext("user_invalid_credentials")}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": gettext("user_logged_out").format(user_id)}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
