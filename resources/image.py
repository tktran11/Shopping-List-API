import os
import traceback

from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from flask_uploads import UploadNotAllowed

from libs import image_handler
from libs.strings import gettext
from schemas.image import ImageSchema

image_schema = ImageSchema()


class ImageUpload(Resource):
    @classmethod
    @jwt_required
    def post(cls):

        data = image_schema.load(request.files)  # {"image": FileStorage}
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"  # static/images/user_id#
        try:
            image_path = image_handler.save_image(data["image"], folder=folder)
            basename = image_handler.get_basename(image_path)
            return {"message": gettext("image_uploaded").format(basename)}, 201
        except UploadNotAllowed:
            extension = image_handler.get_extension(data["image"])
            return (
                {"message": gettext("image_illegal_extension").format(extension)},
                400,
            )


class Image(Resource):
    @classmethod
    @jwt_required
    def get(cls, filename: str):
        """Returns requested image if it exists. Looks up inside the logged in
        user's folder."""
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        if not image_handler.is_filename_safe(filename):
            return {"message": gettext("image_illegal_filename").format(filename)}, 400
        try:
            return send_file(image_handler.get_path(filename, folder=folder))
        except FileNotFoundError:
            return {"message": gettext("image_not_found").format(filename)}, 404

    @classmethod
    @jwt_required
    def delete(cls, filename: str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        if not image_handler.is_filename_safe(filename):
            return {"message": gettext("image_illegal_filename").format(filename)}, 400

        try:
            os.remove(image_handler.get_path(filename, folder=folder))
            return {"message": gettext("image_deleted").format(filename)}, 200
        except FileNotFoundError:
            return {"message": gettext("image_not_found").format(filename)}, 404
        except:
            traceback.print_exc()
            return {"message": gettext("image_delete_failed")}, 500


class ProfileUpload(Resource):
    @classmethod
    @jwt_required
    def put(cls):
        """This endpoint is used to upload user avatars, which are named after user's IDs.
        For example: user_{id}.{ext}
        Uploading a new avatar overwrites the existing one."""

        data = image_schema.load(request.files)
        filename = f"user_{get_jwt_identity()}"
        folder = "profile_pictures"
        profile_path = image_handler.find_image_any_format(filename, folder)
        if profile_path:
            try:
                os.remove(profile_path)
            except:
                return {"message": gettext("profile_delete_failed")}, 500

        try:
            ext = image_handler.get_extension(data["image"].filename)
            profile = filename + ext
            profile_path = image_handler.save_image(
                data["image"], folder=folder, name=profile
            )
            basename = image_handler.get_basename(profile_path)
            return {"message": gettext("profile_uploaded").format(basename)}, 200
        except UploadNotAllowed:
            extension = image_handler.get_extension(data["image"])
            return (
                {"message": gettext("image_illegal_extension").format(extension)},
                400,
            )


class Profile(Resource):
    @classmethod
    def get(cls, user_id: int):
        folder = "profile_pictures"
        filename = f"user_{user_id}"
        profile = image_handler.find_image_any_format(filename, folder)
        if profile:
            return send_file(profile)
        return {"message": gettext("profile_not_found")}, 404
