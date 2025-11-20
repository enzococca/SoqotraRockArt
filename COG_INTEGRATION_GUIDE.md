# Guida Integrazione COG (Cloud Optimized GeoTIFF)

## ✅ Completato

1. ✅ Ortofoto convertita in formato COG
2. ✅ File caricato su Dropbox: `/Volumes/Extreme Pro/Dropbox/Soqotra/tiles/orthophoto_shp042_cog.tif`
3. ✅ Dimensione ottimizzata: 66MB (compressione JPEG 85%)

## 📋 Prossimi Passi

### Step 1: Ottieni Link Dropbox

1. Apri Dropbox (web o app)
2. Naviga in: `Soqotra/tiles/`
3. Tasto destro su `orthophoto_shp042_cog.tif` → "Condividi" → "Crea link"
4. Copia il link (es: `https://www.dropbox.com/scl/fi/xxxxx/orthophoto_shp042_cog.tif?rlkey=xxxxx&dl=0`)
5. **IMPORTANTE**: Modifica il link per download diretto:
   - Da: `?rlkey=xxxxx&dl=0`
   - A: `?rlkey=xxxxx&dl=1`

### Step 2: Aggiungi Environment Variable

Nel file `.env` (locale) o su Render (production):

```bash
DROPBOX_COG_URL=https://www.dropbox.com/scl/fi/xxxxx/orthophoto_shp042_cog.tif?rlkey=xxxxx&dl=1
```

### Step 3: Installa Dipendenze JavaScript

Aggiungi nel template HTML (prima del tag `</body>`):

```html
<!-- GeoTIFF e Leaflet-GeoRaster -->
<script src="https://unpkg.com/geotiff@2.0.7/dist-browser/geotiff.js"></script>
<script src="https://unpkg.com/georaster@1.5.6/dist/georaster.browser.bundle.min.js"></script>
<script src="https://unpkg.com/georaster-layer-for-leaflet@3.8.0/dist/georaster-layer-for-leaflet.min.js"></script>
```

### Step 4: Codice JavaScript per Caricare il COG

```javascript
// Inizializza la mappa Leaflet
var map = L.map('map').setView([12.5, 54.0], 13);

// Aggiungi layer base (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Carica il COG da Dropbox
fetch('/api/cog-url')  // Endpoint che restituisce DROPBOX_COG_URL
    .then(response => response.json())
    .then(data => {
        const cogUrl = data.url;

        // Parse GeoTIFF
        parseGeoraster(cogUrl).then(georaster => {
            console.log("GeoTIFF caricato:", georaster);

            // Crea layer GeoRaster
            var layer = new GeoRasterLayer({
                georaster: georaster,
                opacity: 0.8,
                resolution: 256  // Risoluzione tiles
            });

            layer.addTo(map);

            // Zoom sulla bounds del raster
            map.fitBounds(layer.getBounds());
        });
    })
    .catch(error => {
        console.error("Errore caricamento COG:", error);
    });
```

### Step 5: Endpoint Flask per COG URL

In `app.py`, aggiungi:

```python
@app.route('/api/cog-url')
def get_cog_url():
    """Return COG URL from environment."""
    cog_url = os.getenv('DROPBOX_COG_URL')
    if not cog_url:
        return jsonify({'error': 'COG URL not configured'}), 500
    return jsonify({'url': cog_url})
```

### Step 6: Alternativa - Proxy via Flask

Se Dropbox ha problemi CORS, usa un proxy:

```python
@app.route('/cog/<path:filename>')
def serve_cog(filename):
    """Proxy COG from Dropbox."""
    cog_url = os.getenv('DROPBOX_COG_URL')
    if not cog_url:
        return "COG not configured", 500

    # Stream da Dropbox
    response = requests.get(cog_url, stream=True)

    def generate():
        for chunk in response.iter_content(chunk_size=8192):
            yield chunk

    return Response(
        generate(),
        content_type=response.headers.get('Content-Type', 'image/tiff'),
        headers={
            'Access-Control-Allow-Origin': '*'
        }
    )
```

Poi nel JavaScript:

```javascript
parseGeoraster('/cog/orthophoto_shp042_cog.tif').then(georaster => {
    // ... resto del codice
});
```

## 🎨 Template HTML Completo

```html
<!DOCTYPE html>
<html>
<head>
    <title>Soqotra Rock Art - Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        #map {
            height: 600px;
            width: 100%;
        }
    </style>
</head>
<body>
    <h1>Mappa Rock Art - SHP042</h1>
    <div id="map"></div>

    <!-- Leaflet -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <!-- GeoTIFF Libraries -->
    <script src="https://unpkg.com/geotiff@2.0.7/dist-browser/geotiff.js"></script>
    <script src="https://unpkg.com/georaster@1.5.6/dist/georaster.browser.bundle.min.js"></script>
    <script src="https://unpkg.com/georaster-layer-for-leaflet@3.8.0/dist/georaster-layer-for-leaflet.min.js"></script>

    <script>
        // Inizializza mappa
        var map = L.map('map').setView([12.5, 54.0], 13);

        // Base layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap'
        }).addTo(map);

        // Carica COG
        fetch('/api/cog-url')
            .then(r => r.json())
            .then(data => {
                parseGeoraster(data.url).then(georaster => {
                    var layer = new GeoRasterLayer({
                        georaster: georaster,
                        opacity: 0.8,
                        resolution: 256
                    });
                    layer.addTo(map);
                    map.fitBounds(layer.getBounds());
                });
            });

        // Aggiungi marker dei punti rock art
        fetch('/api/points')
            .then(r => r.json())
            .then(points => {
                points.forEach(point => {
                    if (point.latitude && point.longitude) {
                        L.marker([point.latitude, point.longitude])
                            .bindPopup(`<b>${point.motif}</b><br>${point.site}`)
                            .addTo(map);
                    }
                });
            });
    </script>
</body>
</html>
```

## 🚀 Performance

**COG vs Tiles:**
- ✅ 1 file da caricare (66MB) vs migliaia di tiles
- ✅ Streaming progressivo (carica solo le parti visibili)
- ✅ Overviews automatici per zoom out veloce
- ✅ Nessuna pre-generazione richiesta
- ✅ Funziona perfettamente con Dropbox

**Tempi di caricamento stimati:**
- Prima visualizzazione: 3-5 secondi
- Zoom/pan successivi: < 1 secondo
- Cache browser: istantaneo

## ⚠️ Note Importanti

1. **CORS**: Se Dropbox blocca CORS, usa il proxy Flask
2. **Caching**: Il browser cachierà il COG, aggiornamenti richiedono cache clear
3. **Compressione**: JPEG quality 85 è ottimale (buona qualità, dimensioni ridotte)
4. **Dropbox Bandwidth**: Dropbox ha limiti di bandwidth, considera un CDN per alto traffico

## 🔧 Troubleshooting

### COG non si carica
**Causa**: Link Dropbox non corretto o CORS bloccato
**Soluzione**:
1. Verifica che il link termini con `dl=1`
2. Usa il proxy Flask se persiste

### Immagine pixelata
**Causa**: Risoluzione troppo bassa
**Soluzione**: Aumenta `resolution` da 256 a 512 nel GeoRasterLayer

### Caricamento lento
**Causa**: File grande o connessione lenta
**Soluzione**:
1. Riduci qualità JPEG (regenera COG con QUALITY=75)
2. Usa CDN invece di Dropbox

---

**Creato**: 2025-11-20
**Versione**: 1.0
**COG File**: `orthophoto_shp042_cog.tif` (66MB)
