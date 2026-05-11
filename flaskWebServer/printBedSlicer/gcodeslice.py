import subprocess
import tempfile
import os
from pathlib import Path

PRUSASLICER_BIN = "/usr/local/bin/prusa-slicer"  # or "flatpak run com.prusa3d.PrusaSlicer"
PROFILE_INI = "prusa_mini_pen_plotter.ini"


def slice_svg(svg_path: str, output_path: str = None, z_lift_mm: float = 2.0, draw_speed: int = 30) -> str:
    """
    Slices an SVG file using PrusaSlicer CLI and returns the path to the output gcode.

    Args:
        svg_path:    Path to the input .svg file.
        output_path: Where to write the .gcode. If None, writes next to the SVG.
        z_lift_mm:   How high (mm) to lift the pen between strokes.
        draw_speed:  Drawing speed in mm/s.

    Returns:
        Absolute path to the generated .gcode file.

    Raises:
        FileNotFoundError: If the SVG or PrusaSlicer binary doesn't exist.
        RuntimeError:      If PrusaSlicer returns a non-zero exit code.
    """
    svg_path = Path(svg_path).resolve()
    if not svg_path.exists():
        raise FileNotFoundError(f"SVG not found: {svg_path}")
    if not Path(PRUSASLICER_BIN).exists():
        raise FileNotFoundError(f"PrusaSlicer binary not found: {PRUSASLICER_BIN}")

    if output_path is None:
        output_path = svg_path.with_suffix(".gcode")
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        PRUSASLICER_BIN,
        "--load", PROFILE_INI,
        "--retract-lift", str(z_lift_mm),
        "--perimeter-speed", str(draw_speed),
        "--export-gcode",
        "--output", str(output_path),
        str(svg_path),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"PrusaSlicer failed (exit {result.returncode}):\n{result.stderr.strip()}"
        )

    return str(output_path)

if __name__ == '__main__':
    # Only need os for testing
    import os
    print("Current executing directory " + str(os.getcwd()))
    print("Print testing function")
    filename = os.getcwd() + "/testSVG/ZigZagLine.svg"

    slice_svg(filename, "./", 2.0, 30)