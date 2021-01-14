import pytest 
from pathlib import Path 
from PIL import Image
import fairyimage as fi
import numpy as np

_this_folder = Path(__file__).absolute().parent

def _gen_images(size=(32, 32), count=16):
    return [ Image.new(mode="RGB", size=size, color=0) for _ in range(count)]


def test_basic(): 
    images = _gen_images(size=(32, 32), count=6 * 6)
    images = fi.ImageArray(images)
    images = images.reshape((6, 6))

    # `ImageArray` acts like `PIL.Image`. 
    path = _this_folder / "sample.png"
    images.save(path)
    assert path.exists()

    # What happens if `images` are given to `np.ndarray` ? 
    # fi.frame()

def test_init(): 

    # When `np.array's Image is given, shape is maintained.`
    in_data = np.empty((6, 3), dtype=object)
    for y in range(6):
        for x in range(3):
            in_data[y][x] = Image.new(mode="RGB", size=(32, 32), color=0)
    assert fi.ImageArray(in_data).shape == (6, 3)


def test_reshape():
    """Perform `ImageArray.reshape` 's test. 
    """

    # When `fill` is `None`. 
    images = _gen_images(size=(32, 32), count=6 * 6)
    images = fi.ImageArray(images)
    
    assert images.reshape((6, 6)).shape == (6, 6) , "basic"
    assert images.reshape((2, 18)).shape == (2, 18), "basic" 

    assert images.reshape((6, -1)).shape == (6, 6), "-1's handling" 

    with pytest.raises(ValueError):
        # cannot reshape. 
        images.reshape((5, -1))

    with pytest.raises(ValueError):
        # shape's dimension
        images.reshape((6, 6, 1))


    # When `fill` is `True` or specified.
    images = _gen_images(size=(32, 32), count=6 * 6)
    images = fi.ImageArray(images)
    assert images.reshape((6, 6), fill=True).shape == (6, 6), "basic"
    assert images.reshape((2, 18), fill=True).shape == (2, 18), "basic"
    assert images.reshape((5, -1), fill=True).shape == (5, 8), "-1's handling"
    assert images.reshape((-1, 7), fill=True).shape == (6, 7), "-1's handling"

    with pytest.raises(ValueError):
        # shape's dimension
        images.reshape((-1, -1), fill=True)

def test_map():
    """Test map func.
    """
    images = _gen_images(size=(32, 32), count=6 * 6)
    images = fi.ImageArray(images)
    def mock_func(image):
        return image
    out_images = images.map(mock_func)
    assert isinstance(images, fi.ImageArray)
    assert images.shape == out_images.shape


def test_grid():
    """Test map func.
    """
    images = _gen_images(size=(32, 32), count=6 * 6)
    images = fi.ImageArray(images)
    image = images.grid(color=(255, 0, 0), width=4)
    assert isinstance(image, Image.Image)

    
if __name__ == "__main__":
    pytest.main(["--capture=no"])
