from PIL import Image
from fairyimage.color import Color
from fairyimage.image_array import ImageArray
import numpy as np


def frame(image: Image.Image, color: Color = (0, 0, 0), width: int = 3, inner=False) -> Image.Image:
    """Frame the `image` with `line`.

    Return:
        `PIL.Image`.
        If `inner` is `True`, then the size is equal to given `image`.
        If not, 2 * `width` is added to the each length.
    """
    if isinstance(image, Image.Image):
        return _frame_image(image, color, width, inner)
    elif isinstance(image, ImageArray):
        return _frame_image_array(image, color, width, inner)

    raise ValueError(f"f`{type(image)}` is not accepted as `image`.")


def _frame_image(image: Image.Image, color: Color = (0, 0, 0), width: int = 3, inner=False):
    cv = np.array(Color(color).rgba)
    img = np.array(image.convert("RGBA"))
    if not inner:
        img = np.pad(img, pad_width=((width, width), (width, width), (0, 0)))
    img[:width, :, :] = cv[None, None, :]
    img[-width:, :, :] = cv[None, None, :]
    img[:, :width, :] = cv[None, None, :]
    img[:, -width:, :] = cv[None, None, :]
    return Image.fromarray(img)

def _frame_image_array(images: ImageArray,
                       color: Color = (0, 0, 0),
                       width: int = 3,
                       inner=False):
    """
    The inner line width must be the half of the outer line width. 
    """
    def _inner(image):
        return _frame_image(image, color, width, inner)
    
    return images.map(_inner)


if __name__ == "__main__":
    image = Image.new(mode="L", size=(24, 24), color=255)
    image = frame(image, color=(255, 0, 0), inner=False)
    image.show()
