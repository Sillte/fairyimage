from PIL import Image
from fairyimage.conversion import source  # NOQA
from fairyimage.conversion.source import PygmentsCaller  # NOQA
from figpptx import image_misc
import numpy as np

import matplotlib.pyplot as plt 
from matplotlib.artist import Artist
from matplotlib.figure import Figure
from matplotlib.axes import Axes



def from_source(
    source,
    font_name=None,
    font_size=None,
    lexer="Python",
    style="friendly",
    n_image=1,
    break_criterion=None,
    **options
):
    """Convert source code (typically intended for `Python` ) to `PIL.Image.Image`.

    As for `lexer`, `style`, `font_name`, `font_size`, refer to `pygments`.
    Notice that if you set `n_image` is more than 1,
    the return becomes `List`.
    """

    caller = PygmentsCaller(
        style=style, lexer=lexer, font_name=font_name, font_size=font_size, **options
    )
    if n_image == 1:
        return caller.to_image(source)
    else:
        return caller.to_images(source, n_image, break_criterion=break_criterion)


def from_figure(figure, **kwargs):
    """Convert  `matplotlib.figure.Figure` to `PIL.Image.Image`."""
    return image_misc.fig_to_image(figure, **kwargs)


def from_axes(axes, **kwargs):
    """Convert  `matplotlib.figure.Figure` to `PIL.Image.Image`."""
    is_tight = kwargs.pop("is_tight", True)
    return image_misc.ax_to_image(axes, is_tight, **kwargs)


def from_artists(axes, **kwargs):
    """Convert  `matplotlib.artist.Artists` to `PIL.Image.Image`."""
    is_tight = kwargs.pop("is_tight", True)
    return image_misc.artists_to_image(axes, is_tight, **kwargs)


def from_numpy(array, **kwargs):
    # [TODO] For [0, 1] ndarrays, you may take counter-measure.
    #
    return Image.fromarray(array.astype(np.uint8))



def from_object(arg, **kwargs):
    """Convert to `PIL.Image`, on the basis of `type` of `arg`."""
    if isinstance(arg, Figure):
        return from_figure(arg, **kawrgs)
    elif isinstance(arg, Axes):
        return from_axes(arg, **kawrgs)
    elif isinstance(arg, Artists):
        return from_artists(arg, **kwargs)
    elif isinstance(arg, np.ndarray):
        return from_numpy(arg, **kwargs)
    elif isinstance(arg, str):
        return from_source(arg, **kwargs)
    else:
        raise ValueError("Given arg `(type={type(arg)})` cannot be handled.")


if __name__ == "__main__":
    pass
