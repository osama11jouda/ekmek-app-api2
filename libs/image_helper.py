import re
from typing import Union


from flask_uploads import UploadSet, IMAGES
from werkzeug.datastructures import FileStorage

IMAGE_SET = UploadSet('images', IMAGES)


def save_image(image: FileStorage, folder: str = None, name: str = None) -> str:
    return IMAGE_SET.save(image, folder, name)


def image_path(filename: str, folder: str) -> str:
    return IMAGE_SET.path(filename, folder)


def _retrieve_filename(file: Union[str, FileStorage]) -> str:
    if isinstance(file, FileStorage):
        return file.filename
    return file


def is_filename_safe(file: Union[str, FileStorage]) -> bool:
    filename = _retrieve_filename(file)
    _formats = '|'.join(IMAGES)
    regex = f"^[a-zA-Z0-9][a-zA-Z0-9_()-\.]*\.({_formats})$"
    return re.match(regex, filename) is not None
