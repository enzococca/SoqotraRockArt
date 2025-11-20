#!/usr/bin/env bash
# Helper script to generate tiles for SHP042 orthophoto

set -e

# Configuration
INPUT_TIF="/Volumes/Extreme Pro/Dropbox/Soqotra/Soqotra 2024/SHP042/GIS/Orthophoto/orthophoto_shp042-motifs_cut.tif"
OUTPUT_DIR="/Volumes/extesione4T/SoqotraRockArt/tiles/shp042"
ZOOM_LEVELS="12-18"

echo "======================================================================"
echo "🗺️  Generating Tiles for SHP042 Orthophoto"
echo "======================================================================"
echo ""
echo "This will generate web map tiles from the orthophoto."
echo ""
echo "Input:  $INPUT_TIF"
echo "Output: $OUTPUT_DIR"
echo "Zoom:   $ZOOM_LEVELS"
echo ""
echo "⏱️  Estimated time: 5-15 minutes (depending on system)"
echo "💾 Expected output: ~500-1000 MB of tiles"
echo ""
read -p "Press Enter to start or Ctrl+C to cancel..."
echo ""

# Generate tiles
python3 /Volumes/extesione4T/SoqotraRockArt/generate_tiles.py \
  "$INPUT_TIF" \
  "$OUTPUT_DIR" \
  --zoom="$ZOOM_LEVELS" \
  --profile=mercator

echo ""
echo "======================================================================"
echo "✅ Done! Tiles are ready at:"
echo "   $OUTPUT_DIR"
echo ""
echo "Next steps:"
echo "1. Upload $OUTPUT_DIR to Dropbox"
echo "2. Share the folder and get the Dropbox link"
echo "3. Update the web app to use these tiles"
echo "======================================================================"
