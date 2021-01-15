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
![logos_thumbnail.png](static/logos_thumbnail.png)




[tests/test_sample.py](./tests/test_sample.py) is the most basic and fundamental idea of the library is presented, 




