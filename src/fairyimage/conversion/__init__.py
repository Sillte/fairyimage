from fairyimage.conversion import source  #NOQA
from fairyimage.conversion.source import PygmentsCaller  # NOQA

def from_source(source,
                font_name=None,
                font_size=None,
                lexer="Python",
                style="friendly", 
                n_image=1,
                break_criterion=None, 
                **options):

    caller = PygmentsCaller(style=style,
                            lexer=lexer,
                            font_name=font_name, 
                            font_size=font_size,
                            **options)

    if n_image == 1:
        return caller.to_image(source)
    else:
        return caller.to_images(source, n_image, break_criterion=break_criterion) 


if __name__ == "__main__":
    from pathlib import Path
    image = from_source(Path(__file__).read_text())
    image.show()

