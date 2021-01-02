import pytest
from PIL import Image
import fairyimage as fi
import numpy as np


def test_frame():
    """`fairyimage.frame`'s test.
    Especially, focusing on the size of `images`.
    """
    image = Image.fromarray(
        np.random.uniform(0, 255, size=(32, 24, 4)).astype(np.uint8)
    )
    ret_image = fi.frame(image, inner=True, width=3)
    assert ret_image.size == image.size, "Size must be equal."

    ret_image = fi.frame(image, inner=False, width=5)
    assert ret_image.size == (image.size[0] + 10, image.size[1] + 10)


if __name__ == "__main__":
    pytest.main(["--capture=no"])
