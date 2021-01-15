## Development procedures  

## Getting started from `git`.    

We assumes that you `git clone` this repository.  

1. Execute `python ready.py` 
    - You can get a virtual environment `venv` with which this library is installed. 


## Getting started from `cookiecutter`.   

1. Fulfill [./LICENSE](./LICENSE).
    - The template license is [MIT](https://opensource.org/licenses/MIT) .  
    - **Change** the year from which the project starts and Author's name.    

2. Check and revise `README.md`  with knowledge at the present time. 
    - Purpose
    - Install procedure 

3. Perform `git init`.  

Then, basic preparation for development is completed.  


#### Execution of test.

* Execution of test: `pytest`
* Code formatter: `black`, `flake8`. 
* Dependency: See `setup.cfg`. 

#### Functions related to development  

Generally speaking, tests are the most crucial, coding format and type-annotations follow to that.   


* `setuptools` / `pip` : required
    - Command: `pip install .` 
    - Configuration: `setup.cfg`

* `pytest`: strongly recommended.
    - Command: `pytest`
    - Configuration: `pyproject.toml`
    - Purpose: Check the codes and displaying usage to the user.  
    - Comment: Only crude normal case check is desirable. 

* `black`: if possible. 
    - Command: `black`
    - Configuration: `pyproject.toml`
    - Purpose: Coding style check and revision.
    - Comment: It's easy.  

* `flake8`: if possible. 
    - Command: `pytest`
    - Configuration: `flake.ini`
    - Purpose: To eliminate unnecessary or unnatural codes.  

* `mypy`: if possible. 
    - Command: `mypy`
    - Configuration: `mypy.ini`
    - Purpose: To check type annotation.
    - Comment: It maybe a little bit hard to eliminate error completely.  


#### Functions related to development  

* `git`
* `vim` 


