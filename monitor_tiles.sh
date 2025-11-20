#!/usr/bin/env bash
# Monitor tile generation progress

echo "🔄 Monitoring tile generation progress..."
echo ""

while true; do
    clear
    echo "======================================================================"
    echo "🗺️  Tile Generation Monitor"
    echo "======================================================================"
    echo ""
    echo "📊 Current Status:"
    echo ""

    # Count tiles
    TILE_COUNT=$(find tiles/shp042 -name "*.png" 2>/dev/null | wc -l | tr -d ' ')

    # Directory size
    DIR_SIZE=$(du -sh tiles/shp042 2>/dev/null | cut -f1)

    # Zoom levels present
    ZOOM_LEVELS=$(ls -1 tiles/shp042 2>/dev/null | grep -E '^[0-9]+$' | sort -n | tr '\n' ',' | sed 's/,$//')

    # Process status
    if ps aux | grep -q "[g]dal2tiles.py"; then
        PROC_STATUS="🟢 Running"
    else
        PROC_STATUS="🔴 Stopped"
    fi

    echo "   Process Status:    $PROC_STATUS"
    echo "   Tiles Generated:   $TILE_COUNT"
    echo "   Total Size:        $DIR_SIZE"
    echo "   Zoom Levels:       $ZOOM_LEVELS"
    echo ""
    echo "======================================================================"
    echo ""
    echo "Press Ctrl+C to stop monitoring"
    echo ""

    sleep 10
done
