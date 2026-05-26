import subprocess
import tempfile
import os
import re
from pathlib import Path

PRUSASLICER_BIN = "/usr/local/bin/prusa-slicer"
OPENSCAD_BIN = "/usr/bin/openscad"
PROFILE_INI = "prusa_mini_pen_plotter.ini"


def svg_to_stl(svg_path: Path, height_mm: float = 0.2, wall_mm: float = 0.4, stl_name: str = None) -> Path:
    """
    Converts an SVG to STL via OpenSCAD linear_extrude.
    Rotated 90° counter-clockwise around Z-axis.
    For closed shapes (e.g. squares), only the outline is extruded (hollow).
    stl_name controls the output filename so PrusaSlicer embeds the right name in gcode.
    """

    scad_content = (
        f'rotate([0, 0, 90]) '
        f'linear_extrude(height={height_mm}) '
        f'difference() {{'
        f'  import("{svg_path}");'
        f'  offset(r=-{wall_mm}) import("{svg_path}");'
        f'}}'
    )

    with tempfile.NamedTemporaryFile(suffix=".scad", mode="w", delete=False) as f:
        f.write(scad_content)
        scad_path = Path(f.name)

    stl_dir = Path(tempfile.gettempdir())
    stl_filename = f"{stl_name}.stl" if stl_name else scad_path.stem + ".stl"
    stl_path = stl_dir / stl_filename

    result = subprocess.run(
        [OPENSCAD_BIN, "-o", str(stl_path), str(scad_path)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    scad_path.unlink()

    if result.returncode != 0:
        raise RuntimeError(f"OpenSCAD failed:\n{result.stderr.strip()}")

    return stl_path


def slice_svg(svg_path: str, output_path: str = None, chunk_index: int = None, z_lift_mm: float = 2.0, draw_speed: int = 30) -> str:
    svg_path = Path(svg_path).resolve()
    if not svg_path.exists():
        raise FileNotFoundError(f"SVG not found: {svg_path}")
    if not Path(PRUSASLICER_BIN).exists():
        raise FileNotFoundError(f"PrusaSlicer binary not found: {PRUSASLICER_BIN}")

    if chunk_index is not None:
        chunk_name = f"Chunk{chunk_index}"
    else:
        match = re.search(r'(\d+)$', svg_path.stem)
        chunk_name = f"Chunk{match.group(1)}" if match else svg_path.stem

    if output_path is None:
        output_path = svg_path.parent / f"{chunk_name}.gcode"
    else:
        output_path = Path(output_path).resolve()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    stl_path = svg_to_stl(svg_path, stl_name=chunk_name)
    print(f"Slicing {svg_path.name} -> {output_path}")

    try:
        START_GCODE = (
            "M280 P0 S160\n"
            "G4 S1\n"
            "M280 P0 S10\n"
            "G4 S1\n"
            "M280 P0 S90\n"
            "G4 S1\n"
            "G90\n"
            "G4 S1\n"
            "G28\n"
            "G1 Z5 F300\n"
            "G1 X0 Y0 F3000\n"
            "G1 Z0 F300"
        )

        END_GCODE = (
            "G1 Z40"
        )

        cmd = [
            PRUSASLICER_BIN,
            "--load", PROFILE_INI,
            "--start-gcode", START_GCODE,
            "--end-gcode", END_GCODE,
            "--center", "90,90",
            "--retract-lift", str(z_lift_mm),
            "--perimeter-speed", str(draw_speed),
            "--export-gcode",
            "--output", str(output_path),
            "--scale-to-fit", "180,180,1",
            str(stl_path),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
    finally:
        stl_path.unlink()

    if result.returncode != 0:
        raise RuntimeError(
            f"PrusaSlicer failed (exit {result.returncode}):\n{result.stderr.strip()}"
        )

    return str(output_path)


if __name__ == '__main__':
    print("Current executing directory " + str(os.getcwd()))

    svg_dir = Path(os.getcwd()) / "testSVG"
    svg_files = sorted(svg_dir.glob("*.svg"))

    if not svg_files:
        print("No SVG files found.")
    else:
        for i, svg_file in enumerate(svg_files):
            try:
                out = slice_svg(str(svg_file), chunk_index=i, z_lift_mm=2.0, draw_speed=30)
                print(f"  Done: {out}")
            except Exception as e:
                print(f"  Error processing {svg_file.name}: {e}")
