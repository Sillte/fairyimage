"""Using `pygments`, generate
the image of source code.


"""

import sys
from pathlib import Path
from typing import List
from io import BytesIO

import numpy as np
from PIL import Image
from pygments import highlight
from pygments.lexers import find_lexer_class
from pygments.lexers import guess_lexer, guess_lexer_for_filename
from pygments.lexer import Lexer

from fairyimage.conversion import pygments_ext


class PygmentsCaller:
    """

    Low-level usage.
    ------------------

    `Lexer` and `Formatter` is necessary to use `pygments`.
    For `Lexer`, please specify
    """

    default_fontname = "Yu Gothic UI"
    default_fontsize = 18

    def __init__(self, lexer="Python", fontname=None, fontsize=None, **options):
        if fontname is None:
            fontname = self.default_fontname
        if fontsize is None:
            fontsize = self.default_fontsize
        self.lexer = lexer
        self.fontname = fontname
        self.fontsize = fontsize
        self.options = options  # Formatter options.

    def to_image(self, source):
        """To image"""
        lexer = self._yield_lexer(self.lexer, source)
        source = self._to_content(source)
        formatter = pygments_ext.ImageFormatter(
            fontname=self.fontname, fontsize=self.fontsize, **self.options
        )
        buf = BytesIO(highlight(source, lexer, formatter))
        image = Image.open(buf).copy()
        buf.close()
        return image

    def to_images(self, source, n_image=3, break_criterion=None):
        """Return list of images.
        Intuitively, this functions divides the images vertically
        so that it is easy to display the image horizontally.
        """
        lexer = self._yield_lexer(self.lexer, source)
        source = self._to_content(source)
        formatter = pygments_ext.ImageFormatter(
            fontname=self.fontname, fontsize=self.fontsize, **self.options
        )
        divider = pygments_ext.ImageDivider(n_image, break_criterion=break_criterion)
        return divider(source, lexer, formatter)

    def __call__(self, source):
        return self.to_image(source)

    def _to_content(self, arg):
        if isinstance(arg, Path):
            return Path(arg).read_text()
        elif isinstance(arg, str):
            try:
                 path = Path(arg)
                 if path.exists():
                     return path.read_text()
            except Exception: 
                pass
        return arg

    def _yield_lexer(self, lexer, source):
        if isinstance(lexer, Lexer):
            return lexer
        elif isinstance(lexer, str):
            lexer_cls = find_lexer_class(lexer)
            if not lexer_cls:
                raise ValueError(f"Cannot find `{lexer}` Lexer.")
            return lexer_cls()
        elif lexer is None:
            if isinstance(source, Path):
                return guess_lexer_for_filename(source)
            elif isinstance(source, str):
                try:
                    is_file = Path(source).exists()
                except:
                    pass
                else:
                    if is_file:
                        return guess_lexer(source)
        return guess_lexer(source)


def to_image(
    source, fontname=None, fontsize=None, lexer="Python", style="default", **options
):
    """Args:
        source: the content of text.
        lexer: The specifier of `pygments.lexer.Lexer`.
        style: the style
        fontname: The name of font
        fontsize: The font size.

    Note
    --------------------------------
    For customization.
    Other options follow to `pygments.formatters.Formatter`.
    For `style` follow to `https://help.farbox.com/pygments.html`.

    """
    caller = PygmentsCaller(
        style=style, lexer=lexer, fontname=fontname, fontsize=fontsize, **options
    )
    return caller.to_image(source)


def to_images(
    source,
    fontname=None,
    fontsize=None,
    lexer="Python",
    style="default",
    n_image=3,
    concective=None,
    **options
):
    """
    Args:
        n_image(int): the number of image.
        concective(int): If empty lines succeeds `concective` times,
                         it is regarded as the candidates of breaks
                         between images.
    """
    caller = PygmentsCaller(
        style=style, lexer=lexer, fontname=fontname, fontsize=fontsize, **options
    )
    return caller.to_images(source, n_image=n_image, break_criterion=concective)


if __name__ == "__main__":
    # print(list(get_all_lexers()))
    # 日本語サンプル
    content = Path(__file__).read_text()

    image = to_image(content, fontname=None, line_numbers=False, style="friendly")
    # image.show()
    images = to_images(
        content, n_image=2, fontname=None, line_numbers=False, style="friendly"
    )
    for image in images:
        image.show()
