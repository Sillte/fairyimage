import pytest
from pathlib import Path
from PIL import Image 

import fairyimage  
from fairyimage import from_source  
from fairyimage import conversion 
from fairyimage.conversion import PygmentsCaller 
from fairyimage.conversion.pygments_ext import WinFontCollector


def test_from_source(): 
    script = Path(__file__)
    # Naively, `PIL.Image` is generated. 
    # image is genera
    image = from_source(script)
    assert isinstance(image, Image.Image)

    images = from_source(script, n_image=2)
    assert len(images) == 2
    assert all(isinstance(elem, Image.Image) for elem in images)

def test_from_matplotlib(): 
    import matplotlib.pyplot as plt 
    fig, ax = plt.subplots()
    text = ax.text(0.5, 0.5, "hoge")
    image = conversion.from_figure(fig)
    assert isinstance(image, Image.Image)

    image = conversion.from_axes(ax)
    assert isinstance(image, Image.Image)

    image = conversion.from_artists(text)
    assert isinstance(image, Image.Image)


def test_win_font_controller():
    availables = WinFontCollector.get_availables()
    assert isinstance(availables, list)



if __name__ == "__main__":
    pytest.main([__file__, "--capture=no"])
