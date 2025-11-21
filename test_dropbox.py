#!/usr/bin/env python3
"""Test Dropbox API access with new token."""

import os
import sys

# Chiedi il token
token = input("Incolla il nuovo DROPBOX_ACCESS_TOKEN: ")

try:
    import dropbox
    from dropbox.exceptions import ApiError

    print(f"\n✓ Dropbox library importata")
    print(f"✓ Token length: {len(token)} caratteri")

    # Crea client Dropbox
    dbx = dropbox.Dropbox(token)
    print("✓ Client Dropbox creato")

    # Test 1: Verifica account
    try:
        account = dbx.users_get_current_account()
        print(f"\n✅ Account connesso: {account.name.display_name}")
        print(f"   Email: {account.email}")
    except ApiError as e:
        print(f"\n❌ Errore autenticazione: {e}")
        sys.exit(1)

    # Test 2: Lista file in /Soqotra/tiles/
    print("\n--- Test lista file in /Soqotra/tiles/ ---")
    try:
        result = dbx.files_list_folder('/Soqotra/tiles')
        print(f"✓ Trovati {len(result.entries)} file/cartelle:")
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                size_mb = entry.size / (1024*1024)
                print(f"  📄 {entry.name} ({size_mb:.1f} MB)")
            else:
                print(f"  📁 {entry.name}/")
    except ApiError as e:
        print(f"❌ Errore lista: {e}")

    # Test 3: Verifica file specifici
    print("\n--- Test accesso file COG ---")
    cog_path = '/Soqotra/tiles/orthophoto_shp042_final.tif'
    try:
        metadata = dbx.files_get_metadata(cog_path)
        size_mb = metadata.size / (1024*1024)
        print(f"✅ File trovato: {cog_path}")
        print(f"   Dimensione: {size_mb:.1f} MB")
    except ApiError as e:
        print(f"❌ File non trovato: {e}")
        print(f"   Verifica che il file sia sincronizzato su Dropbox!")

    # Test 4: Crea temporary link per COG
    print("\n--- Test creazione temporary link (per thumbnails) ---")
    try:
        temp_link = dbx.files_get_temporary_link(cog_path)
        print(f"✅ Temporary link creato:")
        print(f"   {temp_link.link[:80]}...")
    except ApiError as e:
        print(f"❌ Errore temporary link: {e}")

    # Test 5: Lista shared links esistenti per COG
    print("\n--- Test shared link esistente (per mappa COG) ---")
    try:
        links = dbx.sharing_list_shared_links(path=cog_path, direct_only=True)
        if links.links:
            url = links.links[0].url
            print(f"✅ Shared link esistente trovato:")
            print(f"   {url}")
            direct_url = url.replace('dl=0', 'dl=1')
            print(f"\n📋 Usa questo per DROPBOX_COG_URL:")
            print(f"   {direct_url}")
        else:
            print(f"⚠️  Nessun shared link esistente")
            print(f"   Devi creare un shared link manualmente:")
            print(f"   1. Apri Dropbox web/app")
            print(f"   2. Vai a /Soqotra/tiles/")
            print(f"   3. Right-click su orthophoto_shp042_final.tif")
            print(f"   4. Share → Create link")
            print(f"   5. Cambia dl=0 a dl=1 nell'URL")
    except ApiError as e:
        print(f"❌ Errore shared links: {e}")

    # Test 6: Test thumbnail
    print("\n--- Test accesso thumbnail ---")
    thumb_path = '/Soqotra/ROCKART DATABASE/thumbnails/thumb__DSC3341.JPG'
    try:
        metadata = dbx.files_get_metadata(thumb_path)
        size_kb = metadata.size / 1024
        print(f"✅ Thumbnail trovato: thumb__DSC3341.JPG")
        print(f"   Dimensione: {size_kb:.1f} KB")

        # Prova a creare temporary link
        temp_link = dbx.files_get_temporary_link(thumb_path)
        print(f"✅ Temporary link per thumbnail funziona!")
    except ApiError as e:
        print(f"❌ Errore thumbnail: {e}")
        print(f"   Percorso: {thumb_path}")

    print("\n" + "="*70)
    print("RIEPILOGO:")
    print("="*70)
    print("Se tutti i test sono OK, il token funziona correttamente.")
    print("Verifica che in Render:")
    print("1. DROPBOX_ACCESS_TOKEN = il token che hai appena testato")
    print("2. DROPBOX_COG_URL = il link con dl=1 mostrato sopra")
    print("3. USE_DROPBOX = true")

except ImportError:
    print("❌ Dropbox library non installata. Installa con: pip install dropbox")
    sys.exit(1)
