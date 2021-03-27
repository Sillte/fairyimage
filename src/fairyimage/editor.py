import numpy as np
from typing import Optional, Union, Tuple, Iterable, List, Dict, Any
from PIL import Image, ImageOps
import io
import matplotlib.pyplot as plt

from fairyimage.color import Color
from fairyimage.image_array import ImageArray
from fairyimage.operations import AlignMode, concatenate, resize, yield_size


def make_logo(
    s: str,
    fontsize: int = 36,
    fontcolor: Color = (0, 0, 0),
    backcolor: Optional[Color] = None,
    margin: Union[float, int] = 0.1,
    *,
    size: Optional[Union[int, Tuple[int, int]]]=None, 
    width: int = None,
    height: int = None,
) -> Image.Image:
    """Making a logo.  

    s: content of string.
    fontsize: the size of font.
    fontcolor: the color of font.
    backcolor: the color of background
    margin: what pixels or percentage is padded 
    size: the spceified size.
    """

    def _to_mcolor(color):
        return tuple(v / 255 for v in color.rgb)

    if backcolor is None:
        backcolor = (0, 0, 0, 0)
    backcolor = Color(backcolor)

    # Solving the parameters of `size`, `height` and `width`.  
    if isinstance(size, int):
        size = (size, size)
    if height is not None and width is not None:
        size = (width, height)

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

    if size: 
        acceptable_region = _from_padded_size(size, margin)
        target = contained(target, acceptable_region)
        background = Image.new("RGBA", size=size, color=backcolor.rgba)
        return put(target , background)
    else:
        b_size = _to_padded_size(target.size, margin)
        background = Image.new("RGBA", size=b_size, color=backcolor.rgba)
        result = put(target, background)
        if width is not None or height is not None:
            size = yield_size(result, height=height, width=width)
            result = result.resize(size)
        return result


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
    t = ax.text(0.01,
                0.01,
                s,
                color=_to_mcolor(color),
                fontsize=fontsize,
                fontfamily="Meiryo",
                fontweight='bold')
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
    if width == 0:
        return image.copy()
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
    if width == 0:
        return image.copy()

    def _inner(image):
        return _frame_image(image, color, width, inner)

    return images.map(_inner)



def contained(image: Image.Image, region: Tuple[int, int]) -> Image.Image:
    """Return the resized `Image.Image`,  

    * The image's fits insize region.
    * The aspect ratio of image is invariant. 

    Note
    ------------------------------------
    Conceptually, this is equivalent to `PIL.Image.thumbnail`.   
    """
    size = image.size
    width, height = size
    if isinstance(region, (int ,float)):
        region = [region, region]
    if len(region) != 2:
        raise ValueError(f"Invalid region specification. `{region}`")
    ratio = min(region[0] / size[0], region[1] / size[1])
    return image.resize((round(size[0] * ratio), round(size[1] * ratio)))


def equalize(images: Union[List[Image.Image], Dict[Any, Image.Image]],
             axis=None, 
             mode="resize"):
    """Equalize the size of images. 

    Args:
        axis: Determines whether `width` should  be equal or `height` should be equal.
              It may be specified by `axis` argument. it is used.
              If `both` or  `all`, then `width` and `height` becomes equal. 

        mode: Specify how to 
            - `AlignMode`: `padding` is performed. 
            - "resize": `resize` is performed.

    Conditions:
    * Aspect ratio is invariant. 
    """

    if isinstance(images, dict):
        keys = list(images.keys())
        values = [images[key] for key in keys]
        result = equalize(values, axis=axis, mode=mode)
        return {key: ret for key, ret in zip(keys, result)}

    sizes = [image.size for image in images]


    if axis is None:
        w_length = min(size[0] for size in sizes)
        w_costs = [abs(1 - w_length / size[0]) for size in sizes]
        w_cost = np.mean(w_costs)
        h_length = min(size[1] for size in sizes)
        h_costs = [abs(1 - h_length / size[1])  for size in sizes]
        h_cost = np.mean(h_costs)
        if np.max(np.max(w_costs)) < 0.08:
            axis = "both"
        elif w_cost < h_cost:
            axis = "width"
        else:
            axis = "height"

    if axis == 0:
        axis = "height"
    elif axis == 1:
        axis = "width"

    if axis in {"both", "all", "height-width"}:
        if mode != "resize":
            print(f"Specified mode is not `resize`, but performed `resize` in `equalize`.")
        width = int(round(np.mean([size[0] for size in sizes])))
        height = int(round(np.mean([size[1] for size in sizes])))
        return [image.resize((width, height)) for image in images]

    if axis not in {"width", "height"}:
        raise ValueError("Invalid specification of axis.", axis)


    if mode == "resize":
        if axis == "width":
            length = min(size[0] for size in sizes)
        else:
            length = min(size[1] for size in sizes)
        r_images = []
        for image in images:
            if axis == "width":
                size = (length, image.size[1] * (length / image.size[0]))
            else:
                size = (image.size[0] * (length / image.size[1]), length)
            size = tuple(map(round, size))
            r_images.append(image.resize(size, Image.BICUBIC))
        return r_images

    try:
        mode = AlignMode(mode)
    except Exception as e:
        print(e)
        pass
    else:

        r_images = []
        if axis == "width":
            length = max(size[0] for size in sizes)
        else:
            length = max(size[1] for size in sizes)

        def _make_c_targets(image, axis, offset, mode):
            size = list(image.size)
            pil_axis = 0 if axis == "width" else 1
            # If offset == 1, then `center` is equal to `START`.
            if offset == 1:
                mode = AlignMode.START
            if mode == AlignMode.START or mode == AlignMode.END:
                size[pil_axis] = offset
                pad = Image.new("RGBA", size=size, color=(255, 255, 255, 0))
                if mode == AlignMode.START:
                    targets = (image, pad)
                if mode == AlignMode.END:
                    targets = (pad, image)
                return targets
            if mode == AlignMode.CENTER:
                s_offset = offset // 2
                s_size = list(size)
                s_size[pil_axis] = s_offset
                s_pad = Image.new("RGBA", size=s_size, color=(255, 255, 255, 0))
                e_offset = offset - s_offset
                e_size = list(size)
                e_size[pil_axis] = e_offset
                e_pad = Image.new("RGBA", size=e_size, color=(255, 255, 255, 0))
                targets = (s_pad, image, e_pad)
                return targets
            raise NotImplementedError("Bug.", mode)


        for image in images:
            if axis == "width":
                offset = length - image.size[0]
            else:
                offset = length - image.size[1]
            if offset: 
                targets = _make_c_targets(image, axis, offset, mode)
                r_images.append(concatenate(targets, axis=axis))
            else:
                r_images.append(image)
        return r_images

    raise ValueError("Invalid specification of mode", mode)


if __name__ == "__main__":
    image = Image.new(mode="L", size=(24, 24), color=255)
    image = frame(image, color=(255, 0, 0), inner=False)
    image.show()
