# Guida Generazione Tiles per Ortofoto

Questa guida spiega come generare tiles web dall'ortofoto per visualizzarle nell'applicazione.

## Perché usare i Tiles?

Le ortofoto sono file molto grandi (centinaia di MB o GB). Caricarle direttamente nel browser:
- ❌ È lento
- ❌ Consuma troppa memoria
- ❌ Non funziona su Render (filesystem effimero)

I **tiles** risolvono questi problemi:
- ✅ L'ortofoto viene divisa in piccole immagini (256x256 px)
- ✅ Il browser carica solo i tiles visibili
- ✅ Performance eccellenti
- ✅ Compatibile con Leaflet/OpenLayers
- ✅ Possono essere serviti da Dropbox

## Prerequisiti

- [x] GDAL installato (già presente via QGIS)
- [x] Python 3
- [x] Ortofoto in formato GeoTIFF

## Step 1: Genera i Tiles

### Metodo Semplice (Consigliato)

Usa lo script helper già configurato:

```bash
cd /Volumes/extesione4T/SoqotraRockArt
./generate_shp042_tiles.sh
```

Questo genererà i tiles nella cartella: `/Volumes/extesione4T/SoqotraRockArt/tiles/shp042`

### Metodo Manuale

Se vuoi personalizzare i parametri:

```bash
python3 generate_tiles.py \
  "/Volumes/Extreme Pro/Dropbox/Soqotra/Soqotra 2024/SHP042/GIS/Orthophoto/orthophoto_shp042-motifs_cut.tif" \
  ./tiles/shp042 \
  --zoom=12-18 \
  --profile=mercator
```

**Parametri**:
- `--zoom=12-18`: Livelli di zoom (12 = lontano, 18 = molto vicino)
- `--profile=mercator`: Proiezione Web Mercator (standard per web map)

**Zoom levels consigliati**:
- `12-16`: Più veloce, meno dettaglio (~300 MB)
- `12-18`: Massimo dettaglio (~1 GB) - **CONSIGLIATO**
- `14-18`: Solo zoom ravvicinati (~500 MB)

## Step 2: Verifica i Tiles

Dopo la generazione, controlla:

```bash
cd tiles/shp042
ls -lh
```

Dovresti vedere:
```
tiles/shp042/
├── 12/              # Zoom level 12
│   ├── 2345/        # X coordinate
│   │   ├── 1234.png # Y coordinate
│   │   └── ...
├── 13/
├── 14/
...
└── 18/
```

**Struttura XYZ**: `{z}/{x}/{y}.png` (standard per tile servers)

## Step 3: Carica su Dropbox

### A. Copia i tiles su Dropbox

```bash
# Opzione 1: Copia tutto
cp -r tiles/shp042 "/Volumes/Extreme Pro/Dropbox/Soqotra/tiles/"

# Opzione 2: Rsync (più veloce per aggiornamenti)
rsync -avh --progress tiles/shp042 "/Volumes/Extreme Pro/Dropbox/Soqotra/tiles/"
```

### B. Ottieni il link Dropbox

1. Vai su Dropbox (web o app)
2. Naviga in `Soqotra/tiles/shp042`
3. Tasto destro → "Condividi" → "Crea link"
4. Copia il link (es: `https://www.dropbox.com/scl/fo/xxxxx?dl=0`)

**IMPORTANTE**: Modifica il link per l'uso diretto:
- Da: `https://www.dropbox.com/scl/fo/xxxxx?dl=0`
- A: `https://dl.dropboxusercontent.com/scl/fo/xxxxx`

## Step 4: Integra nell'Applicazione Web

Ora devi modificare `app.py` per caricare i tiles da Dropbox invece che dal filesystem locale.

### Configurazione Dropbox

Aggiungi nelle environment variables (`.env` o Render):

```bash
DROPBOX_TILES_URL=https://dl.dropboxusercontent.com/scl/fo/xxxxx
```

### Modifica il codice

In `app.py`, modifica la funzione `upload_basemap` per usare tiles esterni:

```python
@app.route('/basemap/tiles/<int:z>/<int:x>/<int:y>.png')
def serve_tile(z, x, y):
    """Serve tiles from Dropbox."""
    dropbox_base = os.getenv('DROPBOX_TILES_URL')
    if dropbox_base:
        # Redirect to Dropbox
        tile_url = f"{dropbox_base}/shp042/{z}/{x}/{y}.png"
        return redirect(tile_url)
    else:
        # Fallback to local files (solo per sviluppo locale)
        tile_path = f"static/basemaps/tiles/shp042/{z}/{x}/{y}.png"
        return send_file(tile_path)
```

### Frontend (JavaScript/Leaflet)

Nel template HTML che mostra la mappa:

```javascript
// Aggiungi il layer con i tiles
L.tileLayer('/basemap/tiles/{z}/{x}/{y}.png', {
    maxZoom: 18,
    minZoom: 12,
    attribution: 'Orthophoto SHP042 - Soqotra Rock Art Project'
}).addTo(map);
```

## Step 5: Test in Locale

Prima di deployare su Render:

```bash
cd /Volumes/extesione4T/SoqotraRockArt
source venv/bin/activate
python app.py
```

Vai su `http://localhost:5000` e carica la mappa. Dovresti vedere l'ortofoto come layer.

## Step 6: Deploy su Render

Dopo aver testato in locale:

```bash
git add .
git commit -m "Add Dropbox tiles integration for orthophoto"
git push origin main
```

Render farà automaticamente il redeploy.

## Troubleshooting

### Errore: "No such file or directory"
**Causa**: Percorso ortofoto errato
**Soluzione**: Verifica che il file esista:
```bash
ls -lh "/Volumes/Extreme Pro/Dropbox/Soqotra/Soqotra 2024/SHP042/GIS/Orthophoto/orthophoto_shp042-motifs_cut.tif"
```

### Tiles non si caricano dalla mappa
**Causa**: URL Dropbox non corretto o tiles non pubblici
**Soluzione**:
1. Verifica che il link Dropbox sia condiviso pubblicamente
2. Controlla la console del browser per errori 403/404
3. Testa manualmente: apri in browser `{DROPBOX_URL}/12/2345/1234.png`

### Generazione troppo lenta
**Causa**: File molto grande o troppi zoom levels
**Soluzione**:
- Riduci zoom: usa `--zoom=14-18` invece di `12-18`
- Usa meno CPU: rimuovi `--processes=4` dallo script

### Troppo spazio su disco
**Causa**: Zoom levels troppo alti (18-20)
**Soluzione**:
- Zoom 18 è sufficiente per la maggior parte dei casi
- Elimina zoom non necessari: `rm -rf tiles/shp042/19 tiles/shp042/20`

## Performance

**Tempo generazione** (stimato per orthophoto 493MB):
- Zoom 12-16: ~5 minuti
- Zoom 12-18: ~10-15 minuti
- Zoom 12-20: ~30+ minuti

**Spazio disco** (stimato):
- Zoom 12-16: ~300 MB
- Zoom 12-18: ~1 GB
- Zoom 12-20: ~3+ GB

**Tip**: Parti con zoom 14-17 per testare, poi rigenera con 12-18 se necessario.

## Comandi Utili

```bash
# Conta i tiles generati
find tiles/shp042 -name "*.png" | wc -l

# Spazio occupato
du -sh tiles/shp042

# Testa un singolo tile
open tiles/shp042/15/12345/6789.png

# Elimina tutti i tiles
rm -rf tiles/shp042
```

## Prossimi Passi

Dopo aver completato questa guida:
1. ✅ Tiles generati localmente
2. ⬜ Tiles caricati su Dropbox
3. ⬜ Link Dropbox configurato in `.env`
4. ⬜ Codice app modificato per usare Dropbox
5. ⬜ Testato in locale
6. ⬜ Deployato su Render

---

**Creato**: 2025-11-20
**Versione**: 1.0
