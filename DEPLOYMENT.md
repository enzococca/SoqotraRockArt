# Deployment su Render.com

Questa guida spiega come deployare l'applicazione Soqotra Rock Art Database su Render.com.

## Prerequisiti

1. Account GitHub con il repository del progetto
2. Account Render.com (gratuito)
3. Token Dropbox API (già configurato)

## File di Configurazione

I seguenti file sono stati preparati per il deployment:

- `build.sh`: Script di build per Render
- `render.yaml`: Configurazione servizio Render
- `requirements.txt`: Dipendenze Python (include dropbox)
- `.env.example`: Template variabili d'ambiente

## Passaggi per il Deployment

### 1. Preparazione Repository GitHub

```bash
# Assicurati di essere nella directory web-app
cd /Volumes/extesione4T/SoqotraDBManager/database-rockart/web-app

# Aggiungi i file al repository (se non già fatto)
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Creazione Servizio su Render

1. Vai su https://render.com e accedi
2. Clicca su "New +" → "Blueprint"
3. Connetti il tuo repository GitHub
4. Seleziona il repository `database-rockart`
5. Render rileverà automaticamente il file `render.yaml`

### 3. Configurazione Variabili d'Ambiente

Dopo aver creato il servizio, vai su **Environment** e aggiungi:

#### Variabili Obbligatorie:

| Nome | Valore | Note |
|------|--------|------|
| `FLASK_ENV` | `production` | Già in render.yaml |
| `SECRET_KEY` | Auto-generato | Già in render.yaml |
| `DATABASE_URL` | Auto-generato | Da PostgreSQL database |
| `USE_DROPBOX` | `true` | Già in render.yaml |
| `DROPBOX_ACCESS_TOKEN` | `sl.u.AGHtkM2V...` | **INSERIRE MANUALMENTE** |

**IMPORTANTE**: Dovrai inserire manualmente il token Dropbox nella dashboard di Render:
1. Environment tab
2. Add Environment Variable
3. Key: `DROPBOX_ACCESS_TOKEN`
4. Value: Il tuo token completo

### 4. Database PostgreSQL

Render creerà automaticamente un database PostgreSQL gratuito:
- Nome: `soqotra-db`
- User: `rockart_user`
- Database: `rockart_db`

Il connection string sarà automaticamente disponibile in `DATABASE_URL`.

### 5. Primo Deploy

1. Il deploy partirà automaticamente dopo la creazione del servizio
2. Controlla i logs nella dashboard Render
3. Aspetta che il build completi (5-10 minuti)

### 6. Migrazione Dati (se necessario)

Se hai già un database SQLite locale e vuoi migrarlo:

```bash
# 1. Esporta dati da SQLite
python export_data.py > data.json

# 2. Importa su PostgreSQL (dopo il deploy)
# Usa il connection string da Render dashboard
export DATABASE_URL="postgresql://..."
python import_data.py data.json
```

### 7. Creazione Primo Utente

Dopo il deploy, crea il primo utente admin:

```bash
# Connettiti al database PostgreSQL da Render shell
# Dashboard → Shell tab

python -c "
from app import app, db, User
with app.app_context():
    user = User(username='admin', email='admin@example.com')
    user.set_password('your-secure-password')
    db.session.add(user)
    db.session.commit()
    print('Admin user created!')
"
```

## Post-Deployment

### Verifica Funzionamento

1. Apri l'URL del servizio (es: `https://soqotra-rockart.onrender.com`)
2. Login con le credenziali create
3. Carica un'immagine di test
4. Verifica che si carichi da Dropbox (controlla i logs)

### Monitoraggio

- **Logs**: Dashboard Render → Logs tab
- **Metrics**: Dashboard Render → Metrics tab
- **Database**: Dashboard Render → Database → Info

### Troubleshooting

#### Errore: "Database connection failed"
- Verifica che `DATABASE_URL` sia configurato correttamente
- Controlla i logs del database

#### Errore: "Dropbox API Error"
- Verifica che `DROPBOX_ACCESS_TOKEN` sia inserito correttamente
- Controlla che il token non sia scaduto
- Verifica i permessi dell'app Dropbox

#### Immagini non si caricano
- Controlla i logs per errori Dropbox
- Verifica che `USE_DROPBOX=true`
- Controlla le cartelle Dropbox esistano

## Costi

### Piano Gratuito Render:
- ✅ 750 ore/mese di web service
- ✅ Database PostgreSQL gratis (90 giorni, poi $7/mese)
- ✅ SSL automatico
- ⚠️ Il servizio va in sleep dopo 15 minuti di inattività

### Upgrade Consigliato (se necessario):
- **Starter Plan**: $7/mese (no sleep, 512MB RAM)
- **PostgreSQL**: $7/mese (dopo trial gratuito)

## Aggiornamenti

Per aggiornare l'applicazione:

```bash
git add .
git commit -m "Update description"
git push origin main
```

Render farà automaticamente il re-deploy.

## Backup

### Database Backup Automatico
Render fa backup automatici del database PostgreSQL.

### Backup Manuale
```bash
# Download backup da Render dashboard
# Database → Backups → Download
```

## Domini Personalizzati

Per usare un dominio personalizzato (es: rockart.soqotra.org):

1. Dashboard → Settings → Custom Domains
2. Aggiungi il dominio
3. Configura DNS secondo istruzioni Render

## Supporto

- Documentazione Render: https://render.com/docs
- Dropbox API Docs: https://www.dropbox.com/developers/documentation
- Issues: Apri issue su GitHub repository

---

**Data deployment**: [da inserire]  
**Versione**: 1.0.0  
**Ultimo aggiornamento**: 2025-11-20
