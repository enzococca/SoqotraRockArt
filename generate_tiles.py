#!/usr/bin/env python3
"""
Script to generate XYZ tiles from orthophoto using GDAL2Tiles.

This script converts the orthophoto GeoTIFF to web-friendly tiles
that can be served via Dropbox or any static file hosting.

Usage:
    python generate_tiles.py <input_tif> <output_dir> [options]

Example:
    python generate_tiles.py "/Volumes/Extreme Pro/Dropbox/.../orthophoto.tif" ./tiles --zoom=12-18
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def generate_tiles(input_tif, output_dir, zoom_levels="12-18", profile="mercator"):
    """
    Generate XYZ tiles from GeoTIFF using gdal2tiles.py

    Args:
        input_tif: Path to input GeoTIFF file
        output_dir: Directory to save tiles
        zoom_levels: Zoom range (e.g., "12-18" for zoom 12 to 18)
        profile: Tile profile (mercator, geodetic, raster)
    """

    # Validate input file
    if not os.path.exists(input_tif):
        print(f"❌ Error: Input file not found: {input_tif}")
        sys.exit(1)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Get file size
    file_size = os.path.getsize(input_tif) / (1024 * 1024)  # MB
    print(f"📁 Input file: {input_tif}")
    print(f"📊 File size: {file_size:.1f} MB")
    print(f"🎯 Output directory: {output_dir}")
    print(f"🔍 Zoom levels: {zoom_levels}")
    print(f"🗺️  Profile: {profile}")
    print()

    # Build gdal2tiles command
    cmd = [
        "gdal2tiles.py",
        "--profile", profile,
        "--zoom", zoom_levels,
        "--processes", "4",  # Use 4 CPU cores
        "--webviewer", "none",  # Don't generate HTML viewer
        "--xyz",  # Generate XYZ tiles (Z/X/Y.png)
        input_tif,
        output_dir
    ]

    print("=" * 70)
    print("🚀 Starting tile generation...")
    print("=" * 70)
    print(f"Command: {' '.join(cmd)}")
    print()

    start_time = time.time()

    try:
        # Run gdal2tiles with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Print output in real-time
        for line in process.stdout:
            print(line, end='')

        process.wait()

        if process.returncode != 0:
            print(f"\n❌ Error: gdal2tiles failed with exit code {process.returncode}")
            sys.exit(1)

        elapsed = time.time() - start_time
        print()
        print("=" * 70)
        print(f"✅ Tile generation completed in {elapsed/60:.1f} minutes!")
        print("=" * 70)

        # Count generated tiles
        tile_count = sum(1 for _ in Path(output_dir).rglob("*.png"))
        dir_size = sum(f.stat().st_size for f in Path(output_dir).rglob('*') if f.is_file()) / (1024 * 1024)

        print(f"📊 Statistics:")
        print(f"   - Tiles generated: {tile_count:,}")
        print(f"   - Total size: {dir_size:.1f} MB")
        print(f"   - Average tile size: {(dir_size / tile_count * 1024):.1f} KB")
        print()
        print(f"📂 Tiles saved to: {output_dir}")
        print()
        print("Next steps:")
        print("1. Upload tiles directory to Dropbox")
        print("2. Get Dropbox shared link for the tiles folder")
        print("3. Update web app to load tiles from Dropbox")

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_tiles.py <input_tif> <output_dir> [--zoom=12-18] [--profile=mercator]")
        print()
        print("Examples:")
        print('  python generate_tiles.py "orthophoto.tif" ./tiles')
        print('  python generate_tiles.py "orthophoto.tif" ./tiles --zoom=14-18')
        print('  python generate_tiles.py "orthophoto.tif" ./tiles --zoom=12-18 --profile=mercator')
        print()
        print("Profiles:")
        print("  - mercator: Web Mercator (Google Maps, OpenStreetMap) - DEFAULT")
        print("  - geodetic: WGS84 Plate Carrée")
        print("  - raster: No reprojection (use original)")
        print()
        print("Zoom levels:")
        print("  - Lower zooms (12-14): Faster, less detail, fewer tiles")
        print("  - Higher zooms (15-18): Slower, more detail, more tiles")
        print("  - Recommended: 12-18 for high-resolution orthophotos")
        sys.exit(1)

    input_tif = sys.argv[1]
    output_dir = sys.argv[2]

    # Parse optional arguments
    zoom_levels = "12-18"
    profile = "mercator"

    for arg in sys.argv[3:]:
        if arg.startswith("--zoom="):
            zoom_levels = arg.split("=")[1]
        elif arg.startswith("--profile="):
            profile = arg.split("=")[1]

    generate_tiles(input_tif, output_dir, zoom_levels, profile)


if __name__ == "__main__":
    main()
