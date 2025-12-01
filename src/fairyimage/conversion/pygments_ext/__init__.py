"""Extensions pertaining to `pygments`.

This is experimental, and I do not have much confidence that the functions below
works correctly,


Environment I write this script. 
-------
* Windows 10
* Python 3.8
* pygment==2.8.1
* Pillow==8.2.0

Note
-------------------------------
`winreg` is only for windows...

"""
from io import BytesIO
from PIL import Image
from PIL import ImageFont, Image
from collections import defaultdict
import re
import sys
import os
import warnings
import winreg
from pathlib import Path
from typing import List, Sequence

import numpy as np
from pygments.formatters.img import FontNotFound
import pygments.formatters.img
from pygments import highlight

from fairyimage.conversion.pygments_ext.win_font import WinFontCollector


class FontManager(pygments.formatters.img.FontManager):
    def __init__(self, fontname=None, fontsize=14):
        if not sys.platform.startswith("win"):
            raise RuntimeError("This class cannot be used except Windows.")

        if fontname is None:
            fontname = "Courier New"

        self.fontname = fontname

        # Windows フォントロード
        self.fonts = WinFontCollector().get_fonts(self.fontname, fontsize)

        # Pygments 2.11+ の新属性に対応
        self.variable = hasattr(self.fonts, "get_style")


class ImageFormatter(pygments.formatters.img.ImageFormatter):
    """

    Extended Features.

    * For solving font related problems, `WinFontCollector` is used for setting the font.

    * Calculate `linelengths: Dict[int, int]` is introduced.
    Via this information, you can get the line nubmers,
    where empty line exist.  which can be used for dividing images vertically.
    """

    default_fontname = "Yu Gothic UI"
    default_fontsize = 18

    def __init__(self, fontname=None, fontsize=18, **options):
        if not fontname:
            fontname = self.default_fontname
        if not fontsize:
            fontsize = self.default_fontsize

        super().__init__(**options)

        # The update related to `font` must be performed.
        self.fonts = FontManager(fontname, fontsize)
        self.fontw, self.fonth = self.fonts.get_char_size()

        if self.line_numbers:
            self.line_number_width = (
                self.fontw * self.line_number_chars + self.line_number_pad * 2
            )
        else:
            self.line_number_width = 0

        # ...
        self.linelengths = None

    def _create_drawables(self, tokensource):
        """
        Create drawables for the token content.
        """
        lineno = charno = maxcharno = 0
        maxlinelength = linelength = 0

        linelengths = []
        for ttype, value in tokensource:
            while ttype not in self.styles:
                ttype = ttype.parent
            style = self.styles[ttype]
            # TODO: make sure tab expansion happens earlier in the chain.  It
            # really ought to be done on the input, as to do it right here is
            # quite complex.
            value = value.expandtabs(4)
            lines = value.splitlines(True)
            # print lines
            for i, line in enumerate(lines):
                temp = line.rstrip("\n")
                if temp:
                    self._draw_text(
                        self._get_text_pos(linelength, lineno),
                        temp,
                        font=self._get_style_font(style),
                        text_fg=self._get_text_color(style),
                        text_bg=self._get_text_bg_color(style),
                    )
                    temp_width, temp_hight = self.fonts.get_text_size(temp)
                    linelength += temp_width
                    maxlinelength = max(maxlinelength, linelength)
                    charno += len(temp)
                    maxcharno = max(maxcharno, charno)
                if line.endswith("\n"):
                    # Below line is added.
                    linelengths.append(linelength)
                    # add a line for each extra line in the value
                    linelength = 0
                    charno = 0
                    lineno += 1
        self.maxlinelength = maxlinelength
        self.maxcharno = maxcharno
        self.maxlineno = lineno

        # Retain linelengths information.
        self.linelengths = linelengths


class PivotsException(Exception):
    """This is raised when it is impossible to divide. (cannot determine `pivots`)"""

    pass


class ImageDivider:
    """Divide one image vertically, using the extended `ImageFormatter`."""

    def __init__(self, n_image, break_criterion=None):
        """
        n_image(int): The number of `image`.
        break_criterion(int): The required concective empty lines
                         to be regarded as the separation of the contents.
        """
        self.n_image = n_image
        self.break_criterion = break_criterion

    def __call__(self, source, lexer, formatter):
        """
        Args:
            content (str): the target.
            lexer (str): Lexe
            formatter (str): pygments_ext.ImageFormatter
        """
        if not isinstance(formatter, ImageFormatter):
            raise ValueError(f"Formatter must be `{pygments_ext.ImageFormatter}`.")

        buf = BytesIO(highlight(source, lexer, formatter))
        image = Image.open(buf).copy()
        buf.close()

        if formatter.linelengths is None:
            raise ValueError(
                f"Formatter' linelength is not yet set. Maybe it is not `formatted`?"
            )

        if self.break_criterion == 0:
            pivots = self._simple_pivots(formatter, self.n_image)
        elif isinstance(self.break_criterion, int) and 1 <= self.break_criterion:
            pivots = self._empty_pivots(
                formatter, self.n_image, concective=self.break_criterion
            )
        elif self.break_criterion is None:
            pivots = self._auto_pivots(formatter, self.n_image)
        else:
            raise PivotsException("Specification of `break_criterion` is illegal.")
        return self._partition(image, formatter, pivots)

    def _partition(self, image, formatter, pivots: List[int]):
        """Partition `image`, at `lines`.

        Args:
            `pivots`:
                Each element is a line number where image is separated.
                Notice that the first and the last are NOT included.

                The first image : [0, pivots[0] - 1].
                The second image: [pivots[1], pivots[2] - 1].
                ...
                the last image: [pivots[n_image - 2], len(formatter.linelengths) - 1]
        """
        linelengths = formatter.linelengths
        array = np.array(image.convert("RGB"))  # (H, W, C)
        result = []
        current_y = 0
        l_height = formatter._get_line_height()
        for lineno in pivots:
            y = formatter._get_line_y(lineno)
            sub_array = array[current_y:y, ...]
            sub_image = Image.fromarray(sub_array)
            result.append(sub_image)
            current_y = y
        result.append(Image.fromarray(array[current_y:, ...]))
        return result

    def _simple_pivots(self, formatter, n_image):
        # This is a crude implementation
        # applicable in many cases.
        # but character is cut down in midway.
        linelengths = formatter.linelengths
        if len(linelengths) < n_image:
            raise PivotsException("The number of lines is lower than `n_image`.")
        n_line = len(linelengths)
        base = n_line // n_image
        remainder = n_line % n_image
        ret = []
        current = 0
        for i in range(n_image):
            ret.append(current)
            current += base + int(i < remainder)
        result = ret[1:]
        assert len(result) == n_image - 1
        return result

    def _empty_pivots(self, formatter, n_image, concective=1):
        """Give the pivots whose linelength is 0."""
        linelengths = formatter.linelengths
        assert concective >= 1
        # When concective is 1, line numbers whose charactors are 0 becomes the candidates.
        # if concective is larger than 1, then if the empty lines successes for `concective`,
        # it is regarded as the candidates.
        if concective == 1:
            cands = [index for index, length in enumerate(linelengths) if length == 0]
        else:
            cands = [
                index
                for index, length in enumerate(
                    linelengths[concective - 1 :], start=concective - 1
                )
                if all(linelengths[index - prev] == 0 for prev in range(concective))
            ]
        if len(cands) < n_image - 1:
            raise PivotsException("Image's empty line is deficit for `n_image`.")

        n_line = len(linelengths)
        terms = [cands[0]]
        for l, r in zip(cands[:-1], cands[1:]):
            terms.append(r - l)
        terms.append(len(linelengths) - cands[-1])

        # cands[0], cands[1], .... are the candidates of separation.
        # terms[0]: `len(lines[0:cands[0]])`
        # terms[k]: `len(lines[cands[k -1]:cands[k]])`.

        # Confirmation.
        # cands[t] = `\sum_{i=0}^{t}terms[i]` holds.
        # \sum_{i=0}terms[i] = n_line holds.
        assert sum(terms[: len(cands)]) == cands[len(cands) - 1]
        assert sum(terms) == len(linelengths)

        # Problem
        # Divide `terms` into `n_image` partitions..
        # Each partition can only include concective terms.
        # Cost function: max_{P \in partion} abs(sum(P) - n_line / n_image)

        def _solve(terms):
            def _cost(p):
                return abs(sum(p) - n_line / n_image)

            # nonlocal variables.
            result_cost = sum(terms)
            result_partitions = None

            def _inner(c_index, remain, cost, partitions):
                """Survey the cost of problems.
                remain: the number of available partition
                cost: the current maximum cost. the return cannot be smaller than this.
                partitions: the current partitions.
                        `[0:partitions[0]]`, `[partitions[0]:partitions[1]]`... becomes the sum of terms.
                """
                nonlocal result_cost, result_partitions
                if remain == 1:
                    last_group = terms[c_index:]
                    cost = max(cost, _cost(last_group))
                    if cost <= result_cost:
                        result_cost = cost
                        result_partitions = list(partitions)
                else:
                    for i in range(c_index, len(terms) - 1):
                        group = terms[c_index : i + 1]
                        n_cost = max(cost, _cost(group))
                        if n_cost >= result_cost:
                            continue
                        else:
                            partitions.append(i + 1)
                            _inner(i + 1, remain - 1, n_cost, partitions)
                            partitions.pop()

            _inner(0, n_image, 0, [])
            return result_partitions

        terms_partition = _solve(terms)
        # This is befause  cands[t] = \sum_{i=0}^{t}terms[i] holds.
        pivots = [cands[elem - 1] for elem in terms_partition]
        assert len(pivots) == n_image - 1
        return pivots

    def _auto_pivots(self, formatter, n_image):
        """Automatically, decide `pivots`,
        This utilizes `PivotsException`.

        Note
        -----
        This is crude in a way `empty_pivots` does not consider the cost.
        You should take into account the ratios.
        """
        concectives = [2, 1]
        for concective in concectives:
            try:
                return self._empty_pivots(formatter, n_image, concective=concective)
            except PivotsException:
                pass
        return self._simple_pivots(formatter, n_image)


if __name__ == "__main__":
    from PIL import Image, ImageFont
    from pygments.lexers import PythonLexer
    from io import BytesIO
    from PIL import Image
    from pathlib import Path
    from pygments.styles import get_all_styles

    styles = list(get_all_styles())

    content = Path(__file__).read_text()
    image_formatter = ImageFormatter(
        fontname="Courier New", style="vim", fontsize=36, line_numbers=True
    )
    buf = BytesIO(highlight(content, PythonLexer(), image_formatter))
    image = Image.open(buf).copy()
    image.save("hoge.png")
    image.show()
