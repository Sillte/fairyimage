from PIL import Image
import numpy as np

import matplotlib.pyplot as plt 
from matplotlib.artist import Artist
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from figpptx import image_misc   # NOQA
from fairyimage.conversion import source  # NOQA
from fairyimage.conversion.source import PygmentsCaller  # NOQA
from fairyimage.conversion.latex import via_matplotlib   # NOQA
from fairyimage.conversion.latex import via_pdf   # NOQA



def from_source(
    source,
    fontname=None,
    fontsize=None,
    lexer="Python",
    style="friendly",
    n_image=1,
    break_criterion=None,
    **options
):
    """Convert source code (typically intended for `Python` ) to `PIL.Image.Image`.

    As for `lexer`, `style`, `fontname`, `fontsize`, refer to `pygments`.
    Notice that if you set `n_image` is more than 1,
    the return becomes `List`.
    """

    caller = PygmentsCaller(
        style=style, lexer=lexer, fontname=fontname, fontsize=fontsize, **options
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


def from_latex(latex, **kwargs):
    # return via_matplotlib(latex, **kwargs)
    return via_pdf(latex, **kwargs)

if __name__ == "__main__":
    pass
