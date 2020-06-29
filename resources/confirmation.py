import traceback
from time import time

from flask import make_response, render_template
from flask_restful import Resource

from libs.mailgun import MailGunException
from libs.strings import gettext
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema

confirmation_schema = ConfirmationSchema()


class Confirmation(Resource):
    # Returns confirmation page (HTML)
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)

        if not confirmation:
            return {"message": gettext("confirmation_not_found")}, 404

        if confirmation.is_expired:
            return {"message": gettext("confirmation_already_expired")}, 400

        if confirmation.is_confirmed:
            return {"message": gettext("confirmation_already_confirmed")}, 400

        confirmation.is_confirmed = True
        confirmation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_page.html", email=confirmation.user.email),
            200,
            headers,
        )


class ConfirmationByUser(Resource):
    # Returns confirmations for a given user (for testing)
    @classmethod
    def get(cls, user_id: int):
        """ Returns confirmations for given user"""
        user = UserModel.find_by_id(user_id)

        if not user:
            return {"message": gettext("User not found.")}, 404

        return (
            {
                "current_time": int(time()),
                "confirmation": [
                    confirmation_schema.dump(each)
                    for each in user.confirmation.order_by(ConfirmationModel.expire_at)
                ],
            },
            200,
        )

    # Handles resending confirmations as necessary
    @classmethod
    def post(cls, user_id: int):
        """ Resend confirmation email"""
        user = UserModel.find_by_id(user_id)

        if not user:
            return {"message": gettext("User not found.")}, 404

        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.is_confirmed:
                    return {"message": gettext("confirmation_already_confirmed")}, 400
                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()

            return {"message": gettext("confirmation_resent")}, 201
        except MailGunException as error:
            return {"message": str(error)}, 500
        except:
            traceback.print_exc()
            return {"message": gettext("confirmation_resend_failure")}, 500
