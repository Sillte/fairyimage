"""This script prepares the development environment for the library.  

Requirement
* `git`. 
"""

from pathlib import Path
import subprocess
import venv
import os

_this_folder = Path(__file__).absolute().parent
_venv_folder = _this_folder / "venv"

def main(clear=True):
    venv.create(_venv_folder, clear=clear, with_pip=True)
    os.chdir(_this_folder)
    # OS dependency. 
    bin_path = _venv_folder / "Scripts"

    env = dict(os.environ)
    env["PATH"] = f"{bin_path};{env['PATH']}"
    def _run(*args, shell=True, **kwargs):
        nonlocal env
        return subprocess.run(*args, shell=True, env=env, **kwargs)
    # Since `setuptools_scm` is used, so `git` is mandatory. 
    if not (_this_folder / ".git").exists():
        _run("git init")
    _run("python -m pip install -U pip", shell=True)
    _run(f"pip install -e .", check=True)


if __name__ == "__main__":
    main()

