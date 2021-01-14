from PIL import Image
from typing import List, Sequence, Tuple, Callable, Iterator
import math
import numpy as np
from fairyimage.color import Color



class ImageArray:
    """This class handles `multiple images`,
    This behaves as `np.array`.

    * This class behaves as `np.array(images)` are given as object.


    Note
    --------

    ### Roles of attributes. 
    `PIL.Image`'s priority is higher than `np.ndarray`.
    (This is because the specific librarie's functions should be preferred.)

    * `size` returns the concatenated size of `Image`, not the total count of `images`.
    """

    def __init__(self, images):
        self._images = self._to_object_array(images)

    @property
    def count(self):
        """Return the count of `images`."""
        return self._images.size

    def _to_object_array(self, images):
        """
        Only one or two dimensions data are accepted.
        """
        if isinstance(images, Image.Image):
            ret = np.empty(1, dtype=object)
            ret[0] = images
            return ret
        elif isinstance(images, Sequence):
            if isinstance(images[0], Image.Image):
                ret = np.empty(len(images), dtype=object)
                for i, elem in enumerate(images):
                    ret[i] = elem
                return ret[..., np.newaxis]
            else:
                assert isinstance(arg[0][0], Image.Image)
                assert all(len(elems) == len(arg[0]) for elems in arg)
                ret = np.empty((len(images), len(images[0])), dtype=object)
                for i, elems in enumerate(images):
                    for j, elem in enumerate(elems):
                        ret[i][j] = elem
                return ret
        elif isinstance(images, Iterator): 
            return self._to_object_array(list(images))
        if isinstance(images, np.ndarray):
            assert images.dtype == object
            return images

        raise ValueError("Currently, unaccepted argument.")

    @property
    def shape(self):
        return self._images.shape

    def reshape(self, shape, fill=None):
        """Reshape `ImageArray`,

        Args:
            `fill`: It specifies behavior when `prod(shape)` is not equal to `prod(self.shape)`.
        """
        # From now on `fill` should be performed.
        def _to_tuple(shape) -> Tuple[int, int]:
            if isinstance(shape, int):
                if shape <= 0:
                    raise ValueError("When `shape` is int, it must be more than 1.")
                return (shape, shape)
            elif isinstance(shape, Sequence):
                if not shape:
                    raise ValueError(f"Empty shape is not accepted.")
                elif len(shape) == 1:
                    return (shape[0], 1)
                elif len(shape) == 2:
                    return tuple(shape)
                else:
                    raise ValueError(
                        f"`len(shape)` must be 1 or 2, but `f{len(shape)}`"
                    )
            raise ValueError(f"Unaccepted `shape` type, `{type(shpae)}`")

        shape = _to_tuple(shape)

        # If `fill` is False, then this method is simple.
        if not fill:
            return ImageArray(np.reshape(self._images, shape))

        def _solve_fill(fill):
            if fill is True:
                return Image.fromarray(np.zeros((1, 1)).astype(np.uint8)).convert(
                    "RGBA"
                )
            if isinstance(fill, Image.Image):
                return fill
            raise ValueError(f"Unaccepted type of `fill`, `{fill}`")

        fill = _solve_fill(fill)

        def _convert(shape):
            """Convert `-1` to the value."""
            if any(v == 0 for v in shape):
                raise ValueError("0 is not accepted as `shape`.")
            if all(v == -1 for v in shape):
                raise ValueError("All the value of `shape` is -1.")

            # No need for modification.
            if all(v >= 1 for v in shape):
                return shape

            # (mi, ci) = (0, 1) or (1, 0), mi is  -1's axis.
            shape = list(shape)
            mi = 0 if shape[0] == -1 else 1
            ci = 1 if mi == 0 else 0
            v = math.ceil(self.count / shape[ci])
            shape[mi] = v
            return shape

        shape = _convert(shape)

        if np.prod(self.shape) > np.prod(shape):
            raise ValueError(
                f"Given shape is `{shape}`, but this array's shape is `{self.shape}`, which is larger."
            )
        elif np.prod(self.shape) == np.prod(shape):
            # Simple case.
            # print(self._images.shape)
            return ImageArray(self._images.reshape(shape))
        else:
            images = list(self._images.ravel())
            elem_size = images[0].size
            fill_list = [
                fill.resize(elem_size) for _ in range(np.prod(shape) - len(images))
            ]
            images = [*images, *fill_list]
            return ImageArray(images).reshape(shape, fill=None)

        raise RuntimeError("This is a bug.")

    def __getattr__(self, key):
        try:
            return getattr(self.image, key)
        except AttributeError:
            pass
        try:
            return getattr(self._images, key)
        except AttributeError:
            pass

    @property
    def image(self) -> Image.Image:
        """Return `PIL.Image` based on the content"""
        if self._images.ndim == 1:
            return _hstack(self._images)
        elif self._images.ndim == 2:
            lines = [_hstack(elems) for elems in self._images]
            return _vstack(lines)
        raise RuntimeError("This is a bug.")

    def map(self, func: Callable[[Image.Image], Image.Image]) -> "ImageArray":
        """Apply `func` to  all the images to `ImageArray`. 
        """
        images = [func(image) for image in self._images.ravel()]
        return ImageArray(images).reshape(shape=self.shape)

    def grid(self,
             color:Color = (0, 0, 0),
             width: int = 4) -> Image.Image:
        """Returns the `grid` image. 
        """
        # For reference orderes.
        from fairyimage import editor
        def _inner(image):
            return editor.frame(image, color=color, width=width // 2, inner=False)
        array = self.map(_inner)
        return editor.frame(array.image, color=color, width=width // 2, inner=False)


def _hstack(images: List[Image.Image]):
    arrays = [np.array(image) for image in images]
    return Image.fromarray(np.hstack(arrays))


def _vstack(images: List[Image.Image]):
    arrays = [np.array(image) for image in images]
    return Image.fromarray(np.vstack(arrays))


if __name__ == "__main__":
    pass
