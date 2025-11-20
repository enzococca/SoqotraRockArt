# Deploy su Render.com - Guida Rapida

## Credenziali Admin di Default

Dopo il primo deploy, puoi fare login con:

- **Username**: `admin`
- **Password**: `SoqotraRockArt2025!`
- **Email**: `admin@soqotra-rockart.org`

⚠️ **IMPORTANTE**: Cambia la password dopo il primo login!

## Step per il Deploy

### 1. Crea Web Service su Render

1. Vai su https://render.com
2. Accedi con GitHub
3. Clicca "New +" → "Web Service"
4. Seleziona il repository `SoqotraRockArt`

### 2. Configurazione

**Build Command**:
```bash
./build.sh
```

**Start Command**:
```bash
gunicorn -w 4 -b 0.0.0.0:$PORT app:app
```

**Environment Variables**:
| Nome | Valore |
|------|--------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | [Clicca Generate] |
| `USE_DROPBOX` | `true` |
| `DROPBOX_ACCESS_TOKEN` | [Il tuo token Dropbox] |

### 3. Database PostgreSQL

**IMPORTANTE**: Usa PostgreSQL, NON SQLite!

SQLite non funziona su Render perché il filesystem è effimero (i dati vengono cancellati ad ogni restart).

1. Nella dashboard del servizio: "Environment" → "Add Database"
2. Seleziona PostgreSQL
3. Piano Free (90 giorni gratis)
4. Render collegherà automaticamente `DATABASE_URL`

### 4. Dopo il Deploy

1. Apri l'URL del servizio (es: `https://soqotra-rockart.onrender.com`)
2. Login con `admin` / `SoqotraRockArt2025!`
3. **Cambia immediatamente la password** nel tuo profilo
4. Crea altri utenti se necessario
5. Carica i dati tramite l'interfaccia web (se hai un database SQLite locale)

### 5. Caricare Dati Esistenti

Se hai un database SQLite locale con i dati:

**Opzione A - Tramite Interfaccia Web** (se implementata):
- Usa la funzione di upload database nell'interfaccia

**Opzione B - Manuale**:
1. Esporta i record dal database SQLite locale in CSV/Excel
2. Importa i record tramite l'interfaccia web

**Opzione C - Script di Migrazione**:
Posso creare uno script Python per migrare i dati da SQLite a PostgreSQL.

## Costi

- **Web Service Free**: 750 ore/mese, va in sleep dopo 15 min di inattività
- **PostgreSQL Free**: 90 giorni gratis, poi $7/mese
- **Upgrade Starter**: $7/mese (no sleep, sempre attivo)

## Troubleshooting

### Errore: "Database connection failed"
- Verifica che PostgreSQL sia collegato
- Controlla `DATABASE_URL` nelle environment variables

### Errore: "Dropbox API Error"
- Verifica che `DROPBOX_ACCESS_TOKEN` sia corretto
- Controlla che il token non sia scaduto

### Immagini non si caricano
- Verifica `USE_DROPBOX=true`
- Controlla i logs per errori Dropbox
- Verifica che le cartelle Dropbox esistano

## Supporto

Per problemi o domande, consulta `DEPLOYMENT.md` per la guida completa.
