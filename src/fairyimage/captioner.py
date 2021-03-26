from typing import Dict, List
import numpy as np
import fairyimage as fi
from PIL import Image 


class Captioner:
    """Present images with words."""

    def __init__(
        self, fontsize=None, backcolor=None, frame_width=None, frame_color=None
    ):
        self.fontsize = fontsize  # The fontsize of logo.
        self.backcolor = backcolor
        self.frame_width = None
        self.frame_color = None

    def __call__(self, word_to_image: Dict[str, Image.Image]):
        # Firstly, I'd like to realize the most crude idea.

        # parameters which may require modification based on `word_to_image`.
        fontsize = self.to_fontsize(self.fontsize, word_to_image)

        word_to_logo = self.make_logos(word_to_image, fontsize)
        images = [
            fi.vstack((word_to_logo[word], word_to_image[word]), align="center")
            for word in word_to_logo
        ]
        return fi.hstack(images)

    def make_logos(self, word_to_image, fontsize) -> Dict[str, Image.Image]:
        word_to_logo = dict()
        for word, _ in word_to_image.items():
            logo = fi.make_logo(word, fontsize=fontsize, backcolor=self.backcolor)
            word_to_logo[word] = logo
        return word_to_logo

    def to_fontsize(self, fontsize, word_to_image):
        if isinstance(fontsize, (int, float)):
            return int(fontsize)
        if fontsize is None:
            sizes = [image.size for image in word_to_image.values()]
            heights = [size[1] for size in sizes]
            widths = [size[0] for size in sizes]
            return round(np.mean(heights + widths) * 0.15)
        raise ValueError("Specification of `fontsize` is invalid.", fontsize)


def captionize(word_to_image: Dict[str, Image.Image]):
    captioner = Captioner()
    return captioner(word_to_image)

