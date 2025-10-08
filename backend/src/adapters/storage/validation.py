from io import BytesIO

from PIL import Image
from fastapi import UploadFile


def validate_image(avatar: UploadFile) -> BytesIO:
    supported_image_formats = {"JPEG", "PNG", "WEBP"}
    max_file_size = 2 * 1024 * 1024

    contents = avatar.file.read()
    if len(contents) > max_file_size:
        raise ValueError("Image size exceeds 2 MB limit")

    try:
        image = Image.open(BytesIO(contents))
    except IOError as e:
        raise ValueError("Invalid image format") from e

    image_format = image.format.upper()
    if image_format not in supported_image_formats:
        raise ValueError(
            f"Unsupported image format: {image_format}. "
            f"Use one of: {', '.join(supported_image_formats)}"
        )

    # Crop to 1:1 aspect ratio
    width, height = image.size
    min_side = min(width, height)
    left = (width - min_side) / 2
    top = (height - min_side) / 2
    right = (width + min_side) / 2
    bottom = (height + min_side) / 2
    image = image.crop((left, top, right, bottom))

    output = BytesIO()
    image.save(output, format=image_format)
    output.seek(0)

    avatar.file.seek(0)

    return output
