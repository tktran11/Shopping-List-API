from dotenv import load_dotenv

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_uploads import configure_uploads, patch_request_class
from marshmallow import ValidationError

from ma import ma
from db import db
from blacklist import BLACKLIST

from resources.user import (
    UserRegister,
    UserLogin,
    User,
    TokenRefresh,
    UserLogout,
)
from resources.item import Item, ItemList, ItemPriorityFind
from resources.shopping_list import ShoppingList, ListOfShoppingLists
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.image import Image, ImageUpload, Profile, ProfileUpload
from libs.image_handler import IMAGE_SET

# Creates and configures the flask application

app = Flask(__name__)
load_dotenv(".env", verbose=True)
app.config.from_object("default_config")
app.config.from_envvar("APPLICATION_SETTINGS")
patch_request_class(app, 10 * 1024 * 1024)  # 10 MB max image upload size for API
configure_uploads(app, IMAGE_SET)

api = Api(app)
jwt = JWTManager(app)


# Creates database before first request to API can be sent
@app.before_first_request
def create_tables():
    db.create_all()


# App-Wide error handling for Validation type errors
@app.errorhandler(ValidationError)
def handle_marshmallow_validation(error):
    return jsonify(error.messages), 400


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return (
        decrypted_token["jti"] in BLACKLIST
    )  # Here we blacklist particular JWTs that have been created in the past.


api.add_resource(Confirmation, "/user_confirmation/<string:confirmation_id>")
api.add_resource(ConfirmationByUser, "/confirmation/user/<int:user_id>")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserRegister, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(ImageUpload, "/upload/image")
api.add_resource(Image, "/image/<string:filename>")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(ItemPriorityFind, "/items/show_priority/<int:priority>")
api.add_resource(ProfileUpload, "/upload/profile")
api.add_resource(Profile, "/profile/<int:user_id>")
api.add_resource(ShoppingList, "/shopping_list/<string:name>")
api.add_resource(ListOfShoppingLists, "/shopping_lists")

if __name__ == "__main__":
    db.init_app(app)  # init sqlalchemy for flask app
    ma.init_app(app)  # init marshmallow for flask app
    app.run(port=5000)
