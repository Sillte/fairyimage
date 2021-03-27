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
    * `make_logo` is used to make an image of characters.
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

    ### Comment.
    Consider the situation where simply you would like to display an image,
    with the background. 
    """
    from fairyimage import make_logo, put
    from PIL import Image

    logo = make_logo("Hello")
    background = Image.new("RGBA", size=(100, 100), color=(255, 0, 0))
    result = put(logo, background)
    assert result.size == background.size

def test_captionize():
    """ ### Content
    * Display an image with the title.

    ### Comment.
    Consider the situation where you would like to display an image
    with the short word(s). 
    """
    from PIL import Image
    from fairyimage import captionize, make_logo, contained
    jp_to_en = {"狐": "Fox", "人狼": "Werewolf", "村人": "Villager"}
    word_to_image = {jp: make_logo(en) for jp, en in jp_to_en.items()}
    word_to_image = {word: contained(image, region=(64, 64)) for word, image in word_to_image.items()}
    image = captionize(word_to_image)
    assert isinstance(image, Image.Image)


def test_equalize():
    """ ### Content
    * It is modified so that the length of images should be the same.

    ### Comment.
    * `AlignMode` / `resize` should be kept in mind  for `equalize`.
    """
    from PIL import Image
    from fairyimage import make_logo, equalize, vstack
    logos = [make_logo(f"{'O'* (index + 1)}", fontcolor=(0, 128, 189)) for index in range(5)]
    logos = equalize(logos, axis="width")
    image = vstack(logos)
    assert isinstance(image, Image.Image)


if __name__ == "__main__":
    pytest.main(["--capture=no"])
