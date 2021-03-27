# fairyimage  

### Purpose

This is a personal practice for handling multiple images.  

### Policy / Features / Limitation 

* The class for handling images, `PIL.Image` is used.  
* The number of images handled in this class is expected to few.     
    - This is because too many images are rarely used for presentation purpose.    
* Interface is as preferrable as it is similar to that of `numpy` . 
* Typing Annotation is insufficient.   
* Flake8 /mypy's modification is insufficient.    

### Install Procedure

#### Pre-requirement
- Python3.8+? 
- Windows10 (Font's related problem...). 

```bat
pip install -e .
```

### Gallery

#### Making a thumbnail of logos.  (`thumbtail`)
```python
from fairyimage import make_logo, thumbnail  
logos = [make_logo(str(n), size=50) for n in range(12)]
image = thumbnail(logos)
image.save("logos_thumbnail.png")
```
![logos_thumbnail](static/logos_thumbnail.png)

#### Making a captions of logos. (`captionize`)

```python
from fairyimage import captionize, make_logo, contained
jp_to_en = {"狐": "Fox", "人狼": "Werewolf", "村人": "Villager"}
word_to_image = {jp: make_logo(en, fontcolor=(255, 0, 0)) for jp, en in jp_to_en.items()}
image = contained(captionize(word_to_image), 300)
image.save("fox_werewolf_villager.png")
```
![fox_werewolf_villager.png](static/fox_werewolf_villager.png)

#### Example of `hstack`, `vstack` and `equalize`. 
```
import fairyimage as fi

black = (0, 0, 0)
green = (102, 205, 170)
red = (255, 0, 0)
parts = [fi.make_logo(f"Im{index}", fontcolor=red) for index in range(3)]
parts = [fi.frame(part, width=3) for part in parts]
parts = fi.equalize(parts)
downs = [
    fi.make_logo("↓", fontcolor=black, backcolor=green, height=parts[0].height)
    for _ in range(3)
]
v_parts = [fi.hstack((down, part)) for down, part in zip(downs, parts)]
parts = fi.equalize(parts)
v_stacked = fi.vstack(v_parts)
h_stacked = fi.hstack(parts)
right = fi.make_logo("→→→→", fontcolor=black, backcolor=green, width=h_stacked.width)
h_stacked = fi.vstack((right, h_stacked))
data = {"vstack": v_stacked, "hstack": h_stacked}
data = fi.equalize(data, mode="center")
image = fi.captionize(data, align="resize")
image.save("vstack_hstack.png")
```


[tests/test_sample.py](./tests/test_sample.py) is the most basic and fundamental idea of the library is presented, 




