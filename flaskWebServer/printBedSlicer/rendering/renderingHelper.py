import sys
import io
from PIL import Image

CAIRO_LIB_AVAIL = False

try:
    import cairosvg
    CAIRO_LIB_AVAIL = True
except ImportError:
    # Handle the case where cairosvg is not installed
    print("NO VISUALS FOR RASPI VERSION")
import matplotlib.pyplot as plt
import time

def display_svg(svg_string: str, scale: float = 2.0, ) -> None:
    """Render an SVG string and display it in a native image viewer."""
    newFig, ax = plt.subplots()
    if CAIRO_LIB_AVAIL:
        png_bytes = cairosvg.svg2png(
            bytestring=svg_string.encode("utf-8"),
            scale=scale,          # render at 2× for crisp, high-DPI output
        )
    img = Image.open(io.BytesIO(png_bytes))
    plt.imshow(img)
    plt.axis('off')
