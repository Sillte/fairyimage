"""Font related functions in windows.

Mainly, this function is intended to substitute part of `pygments.formatters.img.FontManager`.

As of pygments==2.8.1, the construction of `fonts` is not sophisticated in Japanese environment.
(At least, for my environment.)

Especially, handling of `.ttc` file was not realized. 
The classes and functions are mainly intended to realise this purpose.  

Since nomenclature of `ttc` files varies for each case,
I wonder this script works in various environments.  

Nevertheless, if you are familiar with python, 
I believe you can revise it for your environment.

* https://github.com/pygments/pygments/blob/2.8.1/pygments/formatters/img.py#L166


Specification (2021/05/05)
--------------------
* `tag` (str): the string specified in registry, which .is regarded as specifier of font file.
    - For `ttc` files, `&` is typicall used as a separator of `ttf` files... but it's just a guess.


Crucial
---------
At `fontname` of `WinFontController`, `Meiryo` does not work...

"""


from collections import defaultdict
import re
import os
import winreg
from pathlib import Path
from PIL import Image, ImageFont

import numpy as np
from pygments.formatters.img import STYLES
import pygments.formatters.img


# It seems many of ttc files's name are divided by `&`.
def _devide_ttc_value(value_name):
    tags = map(str.strip, re.split(r"&", value_name))
    return [tag for tag in tags]


def _get_ttc_faces(ttc_name) -> int:
    """Return the number of collections of `ttc_files`."""
    windir = os.environ.get("WINDIR")
    p = Path(windir) / "fonts" / ttc_name
    assert p.exists()
    with p.open("br") as fp:
        # The structure of header ~`ttc`(4 bytes) -> VERSION(4-byte)
        fp.seek(4 + 4, os.SEEK_SET)
        n_face = int.from_bytes(fp.read(4), "big")
    return n_face


class WinFontCollector:
    """Collect the information of font.

    Currently, only true map is considered.
    """

    @classmethod
    def get_availables(cls):
        ttf_files, ttf_values, ttc_files, ttc_values = cls._collect()
        specifiers = []
        specifiers += cls._fontnames_from_ttf(ttf_values)
        specifiers += cls._fontnames_from_ttc(ttc_values, ttc_files)
        # In `formatters.img`, only the last parts are modified,
        return specifiers

    @classmethod
    def get_fonts(cls, font_name, font_size):
        """Return `dict` of `fonts`, whose keys are `pygments.formatter.img.STYLES`."""
        ttf_files, ttf_values, ttc_files, ttc_values = cls._collect(font_name=font_name)
        pair_infos = []  # (tag: str, func: callable).
        for ttf_file, ttf_value in zip(ttf_files, ttf_values):
            info = cls._info_from_ttf(ttf_value, ttf_file, font_size)
            pair_infos.append(info)

        for ttc_file, ttc_value in zip(ttc_files, ttc_values):
            # Since `font_name` is specified here, 
            # only related files are considered.
            sub_infos = cls._info_from_ttc(ttc_value, ttc_file, font_size)
            pair_infos += [(tag, func) for tag, func in sub_infos if tag.find(font_name) != -1]

        # General -> Specific.
        targets = ["NORMAL", "ITALIC", "BOLD", "BOLDITALIC"]
        def _to_target(tag, func):
            font = func()
            name, style = font.getname()
            #print("tag" ,tag, name, style)
            result = None
            for target in targets:
                for word in reversed(STYLES[target]):  # Specific to general 
                    if word.lower().find(style.lower()) != -1:
                        result = target
                        break
                if result:
                    break
            del font
            if result:
                return result
            # If `ImageFont.getname()`,  does not work, then `tag` is used.
            for target in targets:
                for word in reversed(STYLES[target]):  # Specific to general 
                    if word and tag.lower().find(word.lower()) != -1:
                        result = target
                if result:
                    break
            return result


        assert STYLES.keys() == set(targets)
        candidates = defaultdict(list)  # Element (tag, func)
        for tag, func in pair_infos:
            target = _to_target(tag, func)
            #print("target", target)
            if target:
                pair = (tag, func)
                candidates[target].append(pair)

        if not candidates["NORMAL"]:  # NORMAL is fundamental.
            # FALLBACK
            print(
                "Cannot find the appropriate `NORMAL` font, so fallback measure is tried."
            )
            candidates["NORMAL"] = [pair_infos[0]]

        style_to_func = dict()  # str: callable.
        # Display warnings.
        for target in targets:
            if len(candidates[target]) == 0:
                print(f"The `{target}` font is not found.")
                continue
            if len(candidates[target]) > 1:
                print(f"Multiple `{target}` styles found, so one is used.")
                tags = [pair[0] for pair in candidates[target]]
                # Consider the shortest one is appropriate. 
                def _key(index):
                    return len(tags[index].replace("(TrueType)", ""))
                index = min(range(len(tags)), key=_key)
                print(f"`target`: `{tags[index]}` is selected from `{tags}`.")
                style_to_func[target] = candidates[target][index][1]
            else:
                style_to_func[target] = candidates[target][0][1]

        result = dict()
        result["NORMAL"] = style_to_func["NORMAL"]
        result["ITALIC"] = style_to_func.get("ITALIC", result["NORMAL"])
        result["BOLD"] = style_to_func.get("BOLD", result["NORMAL"])
        result["BOLDITALIC"] = style_to_func.get(
            "BOLDITALIC", result.get("ITALIC", result.get("BOLD", result["NORMAL"]))
        )

        # Generate font objects.
        fonts = {key: func() for key, func in result.items()}
        return fonts

    @classmethod
    def _collect(self, font_name=None):
        """Collect the informations of keys
        Args:
            font_name: If specified, then the target is limited according to it.
        """
        keynames = [
            (
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows NT\CurrentVersion\Fonts",
            ),
            (
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Fonts",
            ),
            (
                winreg.HKEY_LOCAL_MACHINE,
                r"Software\Microsoft\Windows NT\CurrentVersion\Fonts",
            ),
            (
                winreg.HKEY_LOCAL_MACHINE,
                r"Software\Microsoft\Windows\CurrentVersion\Fonts",
            ),
        ]
        ttf_files = []
        ttf_values = []
        ttc_files = []
        ttc_values = []

        for keyname in keynames:
            try:
                key = winreg.OpenKey(*keyname)
            except FileNotFoundError:
                continue
            _, n_value, _ = winreg.QueryInfoKey(key)
            for v_index in range(n_value):
                value_name, file_name, _ = winreg.EnumValue(key, v_index)
                if font_name:
                    if value_name.find(font_name) == -1:
                        continue
                file_type = Path(file_name).suffix.lower()
                if file_type == ".ttf":
                    ttf_files.append(file_name)
                    ttf_values.append(value_name)
                elif file_type == ".ttc":
                    ttc_files.append(file_name)
                    ttc_values.append(value_name)
                else:
                    continue
            winreg.CloseKey(key)
        return ttf_files, ttf_values, ttc_files, ttc_values

    @classmethod
    def _fontnames_from_ttf(clf, value_names):
        # Terms used in `STYLES` is removed from the specifier.
        specifiers = set()
        for value_name in value_names:
            value_name = value_name.replace("(TrueType)", "")
            for style, keywords in STYLES.items():
                for keyword in keywords:
                    value_name = value_name.replace(keyword, "")
            value_name = value_name.strip()
            specifiers.add(value_name)
        return list(specifiers)

    @classmethod
    def _info_from_ttf(clf, value_name, file_name, font_size):
        """Return (`tag`, `callable`)"""
        tag = value_name.replace("(TrueType)", "")

        def font_open():
            return ImageFont.truetype(file_name, font_size)

        return tag, font_open

    @classmethod
    def _fontnames_from_ttc(clf, value_names, file_names):
        # Terms used in `STYLES` is removed from the specifier.
        specifiers = set()
        invalids = dict()
        # It seems many ttc files's name are divided by `&`.
        ttf_value_names = []
        for value_name, file_name in zip(value_names, file_names):
            tags = _devide_ttc_value(value_name)
            n_face = _get_ttc_faces(file_name)
            if n_face != len(tags):
                invalids[value_name] = (len(tags), n_face)
                continue
            ttf_value_names += tags

        if invalids:
            print(
                f"`{invalids}`, files exist, but cannot be handled for difference between nomenclature and the number of faces"
            )
        return clf._fontnames_from_ttf(ttf_value_names)

    @classmethod
    def _info_from_ttc(clf, value_name, file_name, font_size):
        """Return [(`tag`, `callable`)]
        Notice the return becomes `list`.
        """

        def font_open(index):
            return ImageFont.truetype(file_name, font_size, index=index)

        tags = _devide_ttc_value(value_name)
        funcs = [lambda: font_open(index) for index, tag in enumerate(tags)]
        return list(zip(tags, funcs))

if __name__ == "__main__":
    fonts = WinFontCollector.get_fonts("Meiryo UI", 18)
    for style, font in fonts.items():
        print(font.getname())
    
