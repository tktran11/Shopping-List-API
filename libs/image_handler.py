import os
import re
from typing import Union
from werkzeug.datastructures import FileStorage

from flask_uploads import UploadSet, IMAGES

IMAGE_SET = UploadSet("images", IMAGES)  # sets name and allowed extensions
# Allowed types include jpg, png, gif, peg, etc. (common image types)


# Takes FileStorage, saves it to a folder
def save_image(image: FileStorage, folder: str = None, name: str = None) -> str:
    return IMAGE_SET.save(image, folder, name)


# Takes image name and folder to retrieve full path
def get_path(filename: str = None, folder: str = None):
    return IMAGE_SET.path(filename, folder)


# Takes a filename and finds matching image in any acceptable format
def find_image_any_format(filename: str = None, folder: str = None) -> Union[str, None]:
    for _format in IMAGES:
        image = f"{filename}.{_format}"
        image_path = IMAGE_SET.path(filename=image, folder=folder)
        if os.path.isfile(image_path):
            return image_path
    return None


# Takes FileStorage and returns the file name
def retrieve_image_filename(file: Union[str, FileStorage]) -> str:
    if isinstance(file, FileStorage):
        return file.filename
    return file


# Checks regex to see if string name matches or not
def is_filename_safe(file: Union[str, FileStorage]) -> bool:
    filename = retrieve_image_filename(file)

    allowed_format = "|".join(IMAGES)  # png | jpeg | gif , and so on
    regex = f"^[a-zA-Z0-9][a-zA-Z0-9_()-\.]*\.({allowed_format})$"
    return re.match(regex, filename) is not None


# Return full name of the image in the path
def get_basename(file: Union[str, FileStorage]) -> str:
    filename = retrieve_image_filename(file)
    return os.path.split(filename)[1]


# Returns file extension type
def get_extension(file: Union[str, FileStorage]) -> str:
    filename = retrieve_image_filename(file)
    return os.path.splitext(filename)[1]
