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

#### Making a thumbnail of logos. 
```python
from fairyimage import make_logo, thumbnail  
logos = [make_logo(str(n), size=50) for n in range(12)]
image = thumbnail(logos)
image.save("logos_thumbnail.png")
```
![logos_thumbnail](static/logos_thumbnail.png)

#### Making a captions of logos.

```python
from fairyimage import captionize, make_logo, contained
jp_to_en = {"狐": "Fox", "人狼": "Werewolf", "村人": "Villager"}
word_to_image = {jp: make_logo(en, fontcolor=(255, 0, 0)) for jp, en in jp_to_en.items()}
image = contained(captionize(word_to_image), 300)
image.save("fox_werewolf_villager.png")
```
![fox_werewolf_villager.png](static/fox_werewolf_villager.png)


[tests/test_sample.py](./tests/test_sample.py) is the most basic and fundamental idea of the library is presented, 




