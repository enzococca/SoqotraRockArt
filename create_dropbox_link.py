#!/usr/bin/env python3
"""Create Dropbox shared link for COG file."""

import os
import sys
import dropbox
from dropbox.exceptions import ApiError

def create_shared_link(dropbox_path):
    """Create a shared link for the COG file."""
    token = os.getenv('DROPBOX_ACCESS_TOKEN')
    if not token:
        print("ERROR: DROPBOX_ACCESS_TOKEN not found in environment")
        sys.exit(1)

    dbx = dropbox.Dropbox(token)

    # Dropbox API path format
    api_path = dropbox_path

    print(f"Creating shared link for: {api_path}")

    try:
        # Try to get existing shared link first
        try:
            links = dbx.sharing_list_shared_links(path=api_path, direct_only=True)
            if links.links:
                url = links.links[0].url
                print(f"\n✅ Found existing shared link:")
                print(f"   Original: {url}")
                # Convert dl=0 to dl=1
                direct_url = url.replace('dl=0', 'dl=1')
                print(f"   Direct:   {direct_url}")
                return direct_url
        except ApiError as e:
            if 'not_found' not in str(e):
                raise

        # Create new shared link
        settings = dropbox.sharing.SharedLinkSettings(requested_visibility=dropbox.sharing.RequestedVisibility.public)
        shared_link = dbx.sharing_create_shared_link_with_settings(api_path, settings)
        url = shared_link.url

        print(f"\n✅ Created new shared link:")
        print(f"   Original: {url}")
        # Convert dl=0 to dl=1
        direct_url = url.replace('dl=0', 'dl=1')
        print(f"   Direct:   {direct_url}")

        return direct_url

    except ApiError as e:
        print(f"\n❌ Dropbox API Error: {e}")
        print("\nTry creating the link manually:")
        print("1. Open Dropbox (web or app)")
        print("2. Navigate to: Soqotra/tiles/")
        print("3. Right-click on 'orthophoto_shp042_cog.tif'")
        print("4. Click 'Share' → 'Create link'")
        print("5. Copy the link and change 'dl=0' to 'dl=1'")
        sys.exit(1)

if __name__ == '__main__':
    # The path in Dropbox API format
    dropbox_path = '/tiles/orthophoto_shp042_cog.tif'
    direct_url = create_shared_link(dropbox_path)

    print("\n" + "="*70)
    print("NEXT STEP: Add this URL to Render environment variables")
    print("="*70)
    print(f"\nVariable name: DROPBOX_COG_URL")
    print(f"Variable value: {direct_url}")
    print("\nInstructions:")
    print("1. Go to https://dashboard.render.com")
    print("2. Open your 'soqotra-rockart' web service")
    print("3. Click 'Environment' in the sidebar")
    print("4. Click 'Add Environment Variable'")
    print("5. Add the variable above")
    print("6. Click 'Save Changes'")
    print("\nRender will automatically redeploy with the new variable.")
