from typing import Union, List, Tuple, Optional
from PIL import Image
import numpy as np

from figpptx.image_misc import to_image

from fairyimage import version  # NOQA.
from fairyimage.image_array import ImageArray # NOQA
from fairyimage.editor import frame, make_logo, make_str, put, contained  # NOQA
from fairyimage.editor import equalize  # NOQA
from fairyimage.color import Color  # NOQA
from fairyimage.operations import concatenate, vstack, hstack, resize, AlignMode  # NOQA
from fairyimage.captioner import Captioner, captionize  # NOQA

from fairyimage.conversion import from_source  # NOQA
from fairyimage.conversion.source import PygmentsCaller # NOQA


__version__ = version.version


def thumbnail(
    images: List[Image.Image],
    shape: Tuple[int, int] = None,
    grid_color: Color = (0, 0, 0),
    grid_weight: int = 0,
) -> Image.Image:
    """Generate thumbnail of  `images`.

    Args:
        images: List of images
        shape: the number of rows and columns of

    This function is expected to be complex in order to
    correspond to various types of arguments.
    """
    image_array = ImageArray(images)

    if shape is None:
        # Determine the most appropriate `shape`.
        (u_width, u_height) = image_array.unit_size
        count = image_array.count
        divisions = [n for n in range(1, count + 1) if count % n == 0]
        # (u_width * column) is similar to (u_height * row).
        # (row * column) is equal to `image_array.count`.
        r_float = np.sqrt(count * u_width / u_height)
        row = int(min(divisions, key=lambda r: abs(r - r_float)))
        column = count // row
        shape = (row, column)
    image_array = image_array.reshape(shape)
    image = image_array.grid(color=grid_color, width=grid_weight)
    return image


if __name__ == "__main__":
    pass
