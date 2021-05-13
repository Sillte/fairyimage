import pytest
from PIL import Image
from fairyimage import vstack, hstack, resize
import numpy as np


def test_concatenation():
    """`vstack`, `hstack` and `concatenate` test.
    Focus on the size of image.

    Especially, focusing on the size of `images`.
    """
    image1 = Image.fromarray(
        np.random.uniform(0, 255, size=(32, 24, 4)).astype(np.uint8)
    )
    image2 = Image.fromarray(
        np.random.uniform(0, 255, size=(22, 20, 4)).astype(np.uint8)
    )
    ret = vstack((image1, image2))
    assert ret.mode == "RGBA"
    assert ret.size == (
        max(image1.size[0], image2.size[0]),
        image1.size[1] + image2.size[1],
    )

    ret = hstack((image1, image2))
    assert ret.mode == "RGBA"
    assert ret.size == (
        image1.size[0] + image2.size[0],
        max(image1.size[1], image2.size[1]),
    )

    # AlignMode
    assert hstack((image1, image2), align="center").mode == "RGBA"
    assert hstack((image1, image2), align="start").mode == "RGBA"
    assert hstack((image1, image2), align="end").mode == "RGBA"


def test_resize():
    """Test related to `resize` operations."""
    image = Image.fromarray(
        np.random.uniform(0, 255, size=(32, 24, 4)).astype(np.uint8)
    )
    assert resize(image, 2).size == (image.size[0] * 2, image.size[1] * 2)
    assert resize(image, (20, 12)).size == (20, 12)
    with pytest.raises(ValueError):
        resize(image).size == (24, 32)
    assert resize(image, height=50).size[1] == 50
    assert resize(image, width=40).size[0] == 40


if __name__ == "__main__":
    pytest.main([__file__, "--capture=no"])
