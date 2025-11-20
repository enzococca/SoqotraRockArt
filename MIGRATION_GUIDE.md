# Guida Migrazione Database da SQLite a PostgreSQL

Questo documento spiega come migrare i dati dal tuo database SQLite locale al database PostgreSQL su Render.

## Prerequisiti

1. Hai deployato l'applicazione su Render
2. Hai creato il database PostgreSQL su Render
3. Hai il database SQLite locale con i dati da migrare
4. Hai Python con le dipendenze installate

## Step per la Migrazione

### 1. Ottieni l'URL del Database PostgreSQL

Dalla dashboard Render:
1. Vai su "Dashboard" → Seleziona il tuo database PostgreSQL
2. Clicca su "Info"
3. Copia l'**External Database URL** (NON l'Internal Database URL!)

L'URL sarà simile a:
```
postgresql://rockart_user:password123@dpg-xyz123.oregon-postgres.render.com:5432/rockart_db
```

### 2. Prepara il Database Locale

Assicurati di avere il file SQLite con tutti i dati:
```bash
# Esempio percorso
ls -lh /path/to/your/rockart.db
```

### 3. Esegui lo Script di Migrazione

```bash
# Naviga nella directory del progetto
cd /Volumes/extesione4T/SoqotraRockArt

# Installa le dipendenze (se non già installato)
pip install -r requirements.txt

# Esegui la migrazione
python migrate_sqlite_to_postgres.py \
  /path/to/your/rockart.db \
  "postgresql://user:pass@host:5432/dbname"
```

**Esempio Concreto**:
```bash
python migrate_sqlite_to_postgres.py \
  /Volumes/extesione4T/SoqotraDBManager/database-rockart/web-app/rockart.db \
  "postgresql://rockart_user:abc123...@dpg-xyz.oregon-postgres.render.com:5432/rockart_db"
```

### 4. Cosa Fa lo Script

Lo script migra nell'ordine:
1. ✅ **Users** - Utenti (se esistono nel database locale)
2. ✅ **Rock Art Records** - Record principali
3. ✅ **Images** - Immagini collegate ai record (preserva le foreign keys)
4. ✅ **Type Descriptions** - Descrizioni dei tipi

**Gestione Duplicati**:
- Lo script **non sovrascrive** dati esistenti
- Se un record con stesso `site` e `motif` esiste già, viene skippato
- Gli ID vengono rimappati automaticamente per preservare le relazioni

### 5. Verifica della Migrazione

Output dello script:
```
==================================================================
✅ Migration completed successfully!
==================================================================
📊 Summary:
   - Users:           2
   - Rock Art Records: 1543
   - Images:          2837
   - Type Descriptions: 25
==================================================================
```

### 6. Testa l'Applicazione

1. Vai all'URL della tua app su Render (es: `https://soqotra-rockart.onrender.com`)
2. Login con `admin` / `SoqotraRockArt2025!`
3. Verifica che i record siano presenti
4. Prova a visualizzare le immagini (dovrebbero caricarsi da Dropbox)

## Troubleshooting

### Errore: "Error connecting to PostgreSQL"
**Soluzione**:
- Verifica che l'URL sia quello **External** (non Internal)
- Controlla che il database sia attivo su Render
- Assicurati che l'URL sia tra virgolette nel comando

### Errore: "parent record not found"
**Soluzione**:
- Questo succede se un'immagine riferisce a un record che non esiste
- Lo script skippa automaticamente queste immagini
- Verifica l'integrità del database SQLite locale

### Record duplicati
**Soluzione**:
- Lo script skippa automaticamente i duplicati
- Se vuoi reimportare tutto, svuota prima il database PostgreSQL

### Script troppo lento
**Soluzione**:
- La migrazione elabora in batch ogni 100 record
- Per database molto grandi (>10k record), potrebbe richiedere alcuni minuti
- Attendi il completamento, vedrai il progresso nel terminale

## Note Importanti

⚠️ **Backup Prima della Migrazione**:
Prima di eseguire la migrazione, fai un backup del database PostgreSQL:
- Render fa backup automatici
- Puoi scaricare un backup manuale dalla dashboard

⚠️ **Non Interrompere lo Script**:
Durante la migrazione, non interrompere lo script con Ctrl+C, potresti lasciare il database in uno stato inconsistente.

⚠️ **Immagini su Dropbox**:
Lo script migra solo i **riferimenti** alle immagini (path), non i file fisici.
Assicurati che le immagini siano già caricate su Dropbox.

## Ri-eseguire la Migrazione

Se vuoi ri-eseguire la migrazione da zero:

**Opzione 1** - Elimina tutti i dati PostgreSQL:
```python
# Dalla shell di Render (se disponibile) o via script
from app import app, db
with app.app_context():
    db.drop_all()
    db.create_all()
```

**Opzione 2** - Elimina e ricrea il database su Render:
- Dashboard Render → Database → Settings → Delete Database
- Crea nuovo database PostgreSQL
- Ricollega al web service

## Supporto

Se incontri problemi:
1. Controlla i logs dello script
2. Verifica la connessione al database PostgreSQL
3. Consulta la documentazione di Render: https://render.com/docs/databases

---

**Script creato**: 2025-11-20
**Versione**: 1.0
