import sys
import io
from PIL import Image
import cairosvg
import matplotlib.pyplot as plt
import time

def display_svg(svg_string: str, scale: float = 2.0, ) -> None:
    """Render an SVG string and display it in a native image viewer."""
    newFig, ax = plt.subplots()

    png_bytes = cairosvg.svg2png(
        bytestring=svg_string.encode("utf-8"),
        scale=scale,          # render at 2× for crisp, high-DPI output
    )
    img = Image.open(io.BytesIO(png_bytes))
    plt.imshow(img)
    plt.axis('off')
