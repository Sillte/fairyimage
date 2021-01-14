import numpy as np
from typing import Optional, Union, Tuple, Iterable
from PIL import Image, ImageOps
import io
import matplotlib.pyplot as plt

from fairyimage.color import Color
from fairyimage.image_array import ImageArray


def make_logo(
    s: str,
    fontsize: int = 36,
    fontcolor: Color = (0, 0, 0),
    backcolor: Optional[Color] = None,
    margin: Union[float, int] = 0.1,
    *,
    size: Union[int, int]=None, 
) -> Image.Image:
    """Making a logo.  

    size: the spceified size.
    """

    def _to_mcolor(color):
        return tuple(v / 255 for v in color.rgb)

    if backcolor is None:
        backcolor = (0, 0, 0, 0)
    backcolor = Color(backcolor)

    target = make_str(s, fontsize=fontsize, color=fontcolor)


    def _to_padded_size(size, margin) -> Tuple[int, int]:
        if isinstance(margin, int):
            return (size[0] + margin, size[1] + margin)
        elif isinstance(margin, float):
            size = (
                size[0] * (1 + margin),
                size[1] * (1 + margin),
            )
            return (round(size[0]), round(size[1]))
        else:
            raise NotImplementedError(f"Currently, not implemented type for `margin`.")

    def _from_padded_size(size, margin) -> Tuple[int, int]:
        if isinstance(margin, Iterable):
            margin = [-elem for elem in margin]
        else:
            margin = - margin
        return _to_padded_size(size, margin)

    if size is None:
        b_size = _to_padded_size(target.size, margin)
        background = Image.new("RGBA", size=b_size, color=backcolor.rgba)
        return put(target, background)
    else:
        acceptable_region = _from_padded_size(size, margin)
        target = contained(target, acceptable_region)
        print(target.size)
        background = Image.new("RGBA", size=size, color=backcolor.rgba)
        return put(target , background)

    return put(target, background)


def make_str(s: str, fontsize=48, color: Color = (0, 0, 0)) -> Image.Image:
    """
    Return: Image.Image.
        It has following properties  .
        * The font color is specified by `color`.
        * The boundary box is tighten.
        * Its `mode` is `RGBA`.

    Reference
    -----------
    * https://stackoverflow.com/questions/36191953/matplotlib-save-only-text-without-whitespace

    Note
    -------
    * Currently, completely white `str` is impossible.
    * If fontsize is very large, then it may failed.
    """

    def _to_mcolor(color):
        return [v / 255 for v in color.rgb]

    fig, ax = plt.subplots()
    color = Color(color)
    t = ax.text(0.01, 0.01, s, color=_to_mcolor(color), fontsize=fontsize)
    fig.patch.set_alpha(0.0)
    fig.tight_layout()
    ax.axis("off")
    with io.BytesIO() as buf:
        fig.savefig(buf, tranparent=True, format="png")
        buf.seek(0)
        image = Image.open(buf)
        image.load()
        inv_image = ImageOps.invert(image.convert("RGB"))
        cropped = image.crop(inv_image.getbbox())
    fig.clear()
    return cropped


def put(front: Image.Image, back: Image.Image, align="center"):
    """Put `front` image on `back` image following
    to `align` mode.
    """
    assert align == "center", "Current limitation."
    b_size = back.size
    f_size = front.size
    if align == "center":
        box = ((b_size[0] - f_size[0]) // 2, (b_size[1] - f_size[1]) // 2)
    else:
        raise ValueError(f"Not Impleneted align mode, `{align}`.")
    ret = back.copy()
    ret.paste(front, box=box, mask=front)
    return ret


def frame(
    image: Image.Image, color: Color = (0, 0, 0), width: int = 3, inner=False
) -> Image.Image:
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


def _frame_image(
    image: Image.Image, color: Color = (0, 0, 0), width: int = 3, inner=False
):
    cv = np.array(Color(color).rgba)
    img = np.array(image.convert("RGBA"))
    if not inner:
        img = np.pad(img, pad_width=((width, width), (width, width), (0, 0)))
    img[:width, :, :] = cv[None, None, :]
    img[-width:, :, :] = cv[None, None, :]
    img[:, :width, :] = cv[None, None, :]
    img[:, -width:, :] = cv[None, None, :]
    return Image.fromarray(img)


def _frame_image_array(
    images: ImageArray, color: Color = (0, 0, 0), width: int = 3, inner=False
):
    """
    The inner line width must be the half of the outer line width.
    """

    def _inner(image):
        return _frame_image(image, color, width, inner)

    return images.map(_inner)



def contained(image: Image.Image, region: Tuple[int, int]):
    """Return the resized `Image.Image`,  

    * The image's fits insize region.
    * The aspect ratio of image is invariant. 
    """
    size = image.size
    width, height = size
    if isinstance(region, (int ,float)):
        region = [region, region]
    if len(region) != 2:
        raise ValueError(f"Invalid region specification. `{region}`")
    ratio = min(region[0] / size[0], region[1] / size[1])
    return image.resize((round(size[0] * ratio), round(size[1] * ratio)))


if __name__ == "__main__":
    image = Image.new(mode="L", size=(24, 24), color=255)
    image = frame(image, color=(255, 0, 0), inner=False)
    image.show()
