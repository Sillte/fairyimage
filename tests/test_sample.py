"""This script is expected to perform the following: 

* The first usage for users to feel the gist of `fairyimage`.
* The first tests for the developers to check `fairyimage`.

"""

import pytest
import fairyimage  

def test_logos_thumbnail(): 
    """ ### Content
    * Generate 12 images which displays the number from 0 to 11.
    * It is possible to converted image within the specified size.

    ### Comments
    * `make_logo` is used to
    * `thumbnail` is used to a small version of images.
    """

    from fairyimage import make_logo, thumbnail  
    from PIL import Image
    # `make_logo` makes images of string.
    logos = [make_logo(str(n), size=50) for n in range(12)]
    # `thumbnail` generates a thumbnail version of images.
    image = thumbnail(logos)
    assert isinstance(image, Image.Image)

def test_put():
    """ ### Content
    * Put an image to another image.

    ### Comments.
    Consider the situation where simply you would like to display an image,
    with the background. 
    """
    from fairyimage import make_logo, put
    from PIL import Image

    logo = make_logo("Hello")
    background = Image.new("RGBA", size=(100, 100), color=(255, 0, 0))
    result = put(logo, background)
    assert result.size == background.size


if __name__ == "__main__":
    pytest.main(["--capture=no"])
