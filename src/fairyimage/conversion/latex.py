"""Convert `latex` str to an image.

(2021-03-31)  This sub-module is under development. 
You should consider various ways for conversion.  

"""
from PIL import Image 
import matplotlib.pyplot as plt
from figpptx.image_misc import  artists_to_image

def via_matplotlib(formula, fontsize=18) -> Image.Image:
    #(2021-03-31)  I do not know, but if  `fontsize` is large, then `artists_to_image` works does not work correctly.  
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
    text = fig.text(0, 0.5, f'{formula}', fontsize=base_fontsize)
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


