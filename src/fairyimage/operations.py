"""Operations basic operations are listed here.

"""

from typing import Union, List, Tuple, Optional
from PIL import Image
import numpy as np

from fairyimage import version  # NOQA.
from fairyimage.color import Color  # NOQA


class AlignMode:
    """Specify the mode used for aligning.
    Here,
    * (0, left, top): The starting edge position is aligned.
    * (1, right, bottom): The ending edge position is aligned.
    * (0.5, center, middle): The center position is aligned.
    """

    START = "start"
    CENTER = "center"
    END = "end"

    def __init__(self, mode):
        self._mode = self._to_mode(mode)

    @property
    def mode(self):
        return self._mode

    def _to_mode(self, arg):
        if isinstance(arg, AlignMode):
            return arg.mode
        elif isinstance(arg, (float, int)):
            if arg == 0:
                return AlignMode.START
            elif arg == 0.5:
                return AlignMode.CENTER
            elif arg == 1:
                return AlignMode.END
        elif isinstance(arg, str):
            arg = arg.lower().strip()
            if arg in {"start", "left", "top"}:
                return AlignMode.START
            elif arg in {"half", "center", "middle"}:
                return AlignMode.CENTER
            elif arg in {"end", "right", "bottom"}:
                return AlignMode.END
        raise ValueError("Cannot convert to Mode.", arg)

    @staticmethod
    def __call__(arg) -> Union["AlignMode.START", "AlignMode.CENTER", "AlignMode.END"]:
        if isinstance(arg, (float, int)):
            if arg == 0:
                return AlignMode.START
            elif arg == 0.5:
                return AlignMode.CENTER
            elif arg == 1:
                return AlignMode.END
        elif isinstance(arg, str):
            pass

    def __eq__(self, other):
        return self.mode == AlignMode(other).mode


def concatenate(images: List[Image.Image], axis=0, align=AlignMode("start")):
    """Concatenate the multiple images.

    Args:
        images: the target images for
        axis: 0 -> horizontally, 1 -> vertically.
    """
    if axis == "width":
        axis = 1
    if axis == "height":
        axis = 0
    assert axis in {0, 1}, "Axis must be in {0, 1}"

    c_axis = axis
    nc_axis = 0 if c_axis == 1 else 1

    align = AlignMode(align)

    def _to_array(image):
        if isinstance(image, Image.Image):
            return np.array(image)
        raise ValueError("Cannot convert `image` to np.array.")

    def _to_calibrated(array, length, align):
        def _to_height_width(array, offset):
            if c_axis == 0:
                return (array.shape[0], offset)
            elif c_axis == 1:
                return (offset, array.shape[1])
            raise ValueError("offset", offset)

        margin = array.shape[nc_axis]
        offset = length - margin
        if offset == 0:
            return array

        if align == AlignMode.START:
            height, width = _to_height_width(array, offset)
            pad = Image.new("RGBA", size=(width, height), color=(255, 255, 255, 0))
            pad_array = np.array(pad)
            return np.concatenate((array, pad_array), axis=nc_axis)
        elif align == AlignMode.END:
            height, width = _to_height_width(array, offset)
            pad = Image.new("RGBA", size=(width, height), color=(255, 255, 255, 0))
            pad_array = np.array(pad)
            return np.concatenate((pad_array, array), axis=nc_axis)
        elif align == AlignMode.CENTER:
            s_offset = offset // 2
            e_offset = offset - s_offset
            if s_offset:
                height, width = _to_height_width(array, s_offset)
                s_pad = np.array(
                    Image.new("RGBA", size=(width, height), color=(255, 255, 255, 0))
                )
            else:
                s_pad = None
            height, width = _to_height_width(array, e_offset)
            e_pad = np.array(
                Image.new("RGBA", size=(width, height), color=(255, 255, 255, 0))
            )
            arrays = [elem for elem in (s_pad, array, e_pad) if elem is not None]
            return np.concatenate(arrays, axis=nc_axis)
        raise NotImplementedError("Implementation Error.", align)

    images = [image.convert("RGBA") for image in images]

    array_list = [_to_array(image) for image in images]
    lengths = set(array.shape[nc_axis] for array in array_list)
    length = max(lengths)
    if len(lengths) == 1:
        array = np.concatenate(array_list, axis=c_axis)
        return Image.fromarray(array)
    arrays = [_to_calibrated(array, length, align) for array in array_list]
    array = np.concatenate(arrays, axis=c_axis)
    return Image.fromarray(array)


def vstack(images: List[Image.Image], align=AlignMode("start")):
    return concatenate(images, axis=0, align=align)


def hstack(images: List[Image.Image], align=AlignMode("start")):
    return concatenate(images, axis=1, align=align)


def yield_size(
    image,
    *,
    size: Union[Tuple[int, int], float, None] = None,
    height: Optional[int] = None,
    width: Optional[int] = None,
):

    """Based on the given information, returns the size."""
    if size is None and height is None and width is None:
        size = image.size
    elif size:
        if isinstance(size, (float, int)):
            size = tuple(map(lambda x: round(x * size), image.size))
        else:
            size = size
    elif width is not None and height is not None:
        size = (width, height)
    elif width is not None and height is None:
        height = round(width / image.size[0] * image.size[1])
        size = (width, height)
    elif width is None and height is not None:
        width = round(height / image.size[1] * image.size[0])
        size = (width, height)
    else:
        raise ValueError("Necessary information is not given to `yield_size`. ")
    return size


def resize(
    image: Image.Image,
    size: Union[Tuple[int, int], float, None] = None,
    *,
    height: Optional[int] = None,
    width: Optional[int] = None,
):
    """Resize.
    If `size` is given, it is the same as `PIL.Image.Image.resize`.
    If either `height` or `width` is given, then the other is determined so that aspect is maintained.

    """
    if size is None and height is None and width is None:
        raise ValueError(
            f"In `fairyimage.resize`, you should specify either `size`, `height`, or `width`. "
        )
    size = yield_size(image, size=size, height=height, width=width)
    return image.resize(size)
