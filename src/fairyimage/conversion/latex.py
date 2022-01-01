"""Convert `latex` str to an image.

(2021-03-31)  This sub-module is under development. 
You should consider various ways for conversion.  

"""
import os
import numpy as np
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
from figpptx.image_misc import artists_to_image
from pdf2image import convert_from_path, convert_from_bytes
from fairyimage.color import Color

from pathlib import Path
import subprocess

from fairyimage import vstack
from fairyimage.color import Color

_this_folder = Path(__file__).absolute().parent


def gen_documentclass(fontsize: int = 14):
    DOCUMENT_CLASS = fr"""
    \documentclass[{fontsize}pt,landscape]{{ltjsarticle}}
    """.strip()
    return DOCUMENT_CLASS


def gen_preamble():
    PREAMBLE = rf"""
    \usepackage{{graphicx}}
    \usepackage{{comment}}
    \usepackage{{amsmath,amssymb,amsthm}}
    \usepackage{{amsfonts}}
    \usepackage{{physics}}
    \usepackage{{bbm, bm}}
    \usepackage{{color}}
    \pagestyle{{empty}}
    """.strip()
    return PREAMBLE


def gen_document(text, color: Color = None):
    if color is not None:
        values = [elem / 255 for elem in color.rgb]
        color_command = rf"\color[rgb]{{{values[0]}, {values[1]}, {values[2]}}}"
    else:
        color_command = ""
    doc = rf"""
    \begin{{document}}
    {color_command}
    {text}
    \end{{document}}
    """
    return doc


def via_pdf(text, fontsize: int = 12, dpi: int = 960, color: Color = None):
    path = _this_folder / "__latex__.tex"
    pdf_path = _this_folder / "__latex__.pdf"
    if path.exists():
        os.unlink(path)
    if pdf_path.exists():
        os.unlink(pdf_path)
    if color is not None:
        color = Color(color)

    documentclass = gen_documentclass(fontsize)
    preamble = gen_preamble()
    doc = gen_document(text, color=color)

    lines = [documentclass, preamble, doc]

    path.write_text("\n".join(lines))
    ret = subprocess.run(f"lualatex {path}", shell=True, input="", cwd=path.parent)
    if ret.returncode != 0:
        raise ValueError("Failed to compile the latex.")
    assert ret.returncode == 0
    assert pdf_path.exists()
    images = convert_from_path(pdf_path, transparent=True, dpi=dpi)
    image = vstack(images)

    # Since this image seems large, so
    # `trim` may require a lot of time.
    inv_image = ImageOps.invert(image.convert("RGB"))
    cropped = image.crop(inv_image.getbbox())
    return cropped


def via_matplotlib(formula, fontsize=18) -> Image.Image:
    # (2021-03-31)  I do not know, but if  `fontsize` is large, then `artists_to_image` works does not work correctly.
    # Hence, the size is handled by the change of `dpi`.
    # Here, I assumes `fontsize` is under such premise that `dpi` = 96 by default.
    # Furthermore, to alleviate aliasing, over-sampling is performed.

    base_dpi = 96
    base_fontsize = 18
    sampling_ratio = 2.0
    dpi = fontsize / base_fontsize * base_dpi * sampling_ratio
    fig, ax = plt.subplots(dpi=dpi)
    if not formula.startswith("$"):
        formula = f"${formula}$"
    text = fig.text(0, 0.5, f"{formula}", fontsize=base_fontsize)
    image = artists_to_image(text, is_tight=True)
    if sampling_ratio != 1:
        width = round(image.size[0] / sampling_ratio)
        height = round(image.size[1] / sampling_ratio)
        image = image.resize((width, height), Image.BICUBIC)
    plt.close(fig)
    return image


if __name__ == "__main__":
    image = via_matplotlib(r"\frac{\sqrt{2}^2}{35 - 5} - \sqrt{3} = ?", 72)
    print(image.size)
    image.show()
