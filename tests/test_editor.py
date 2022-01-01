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

def test_equalize():
    """`fairyimage.equlize`'s test.
    Escecially, it focuses on the size of `images`, when `axis` and `mode` is specified. 
    """

    image1 = Image.fromarray(
        np.random.uniform(0, 255, size=(32, 24, 4)).astype(np.uint8)
    )

    image2 = Image.fromarray(
        np.random.uniform(0, 255, size=(30, 28, 3)).astype(np.uint8)
    )

    # Check when mode is "resize".

    sizes = [image.size for image in fi.equalize([image1, image2], axis="width", mode="resize")]
    assert all(sizes[0][0] == size[0] for size in sizes)

    sizes = [image.size for image in fi.equalize([image1, image2], axis="height", mode="resize")]
    assert all(sizes[0][1] == size[1] for size in sizes)

    sizes = [image.size for image in fi.equalize([image1, image2], axis="both", mode="resize")]
    assert all(sizes[0] == size for size in sizes)

    # Check when mode is `align`. 
    modes = ["center", "start", "end"]
    for mode in modes:
        sizes = [image.size for image in fi.equalize([image1, image2], axis="width", mode=mode)]
        assert all(sizes[0][0] == size[0] for size in sizes)

    for mode in modes:
        sizes = [image.size for image in fi.equalize([image1, image2], axis="height", mode="resize")]
        assert all(sizes[0][1] == size[1] for size in sizes)

def test_trim():
    """`fairyimage.trim`'s test.
    Here, we would like to confirm the background is eliminated.
    """
    image = Image.fromarray(
        np.random.uniform(0, 255, size=(32, 24, 4)).astype(np.uint8)
    )

    # Intentionally, append `background`.
    background = Image.fromarray(np.zeros((16, 16, 4)).astype(np.uint8))
    image = fi.vstack((image, background))        
    image = fi.hstack((image, background))
    image = fi.trim(image)
    assert image.size == (24, 32)


if __name__ == "__main__":
    pytest.main(["--capture=no"])
