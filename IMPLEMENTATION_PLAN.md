# Implementation Plan - Multi-Feature Update

## ✅ COMPLETED

### 1. User Roles System
- **File**: `models.py`
- **Changes**:
  - Added `is_approved` field (default: False)
  - Added `role` field (viewer/editor/admin)
  - Helper methods: `is_admin()`, `is_editor()`, `can_view()`

### 2. Public Landing Page
- **File**: `templates/welcome.html`
- **Features**:
  - Professional gradient design
  - Login / Register / Public Viewer buttons
  - Project description
  - Feature highlights with icons

### 3. Database Migration Script
- **File**: `migrations/001_add_user_roles_and_orthophotos.sql`
- **Execute on Render PostgreSQL before deploying new code**

## 🚧 IN PROGRESS - Will be implemented in sequence

### 4. Route Updates (app.py)
- Change `/` → `welcome()` (public landing page)
- Keep `/dashboard` or `/index` for authenticated users
- Add `/public-viewer` route (no auth required)

### 5. Public Viewer Page
- Read-only map and records view
- No authentication required
- Simplified interface

### 6. Admin Panel for Users
- `/admin/users` route
- List pending users
- Approve/reject functionality
- Change user roles

### 7. Admin Panel for Orthophotos
- `/admin/orthophotos` route
- Add new orthophoto (name, Dropbox path)
- Edit/delete existing
- Set active/inactive

### 8. Enhanced Map Popup
- Show full record info in popup
- Display thumbnails inline
- No redirect to detail page
- Download button for each image

### 9. Image Download
- `/download/image/<id>` route
- Stream from Dropbox or static
- Proper content-disposition headers

### 10. Map Zoom Enhancement
- Change `maxZoom` from 19 to 23 (~ 1cm detail)
- Adjust orthophoto resolution accordingly

## 📋 MANUAL STEPS REQUIRED

### Before deploying code changes:

1. **Run SQL migration on Render**:
   ```bash
   # In Render Shell or psql client:
   psql $DATABASE_URL < migrations/001_add_user_roles_and_orthophotos.sql
   ```

2. **Set Dropbox Access Token**:
   - Generate permanent token from Dropbox App Console
   - Update `DROPBOX_ACCESS_TOKEN` environment variable in Render
   - Remove `DROPBOX_COG_URL` (no longer needed)

3. **Verify first user is admin**:
   ```sql
   SELECT id, username, is_approved, role FROM users LIMIT 1;
   ```

## 🔄 DEPLOYMENT ORDER

1. Execute SQL migration ✓
2. Deploy code changes (automatic via git push)
3. Verify welcome page loads at `/`
4. Test public viewer at `/public-viewer`
5. Login and verify admin panel access

## ⚙️ CONFIGURATION NOTES

- **Layers/Orthophotos**: Visual overlays only, do NOT populate database automatically
- **User Registration**: New users require admin approval before access
- **Roles**:
  - `viewer`: Read-only access (after approval)
  - `editor`: Can create/edit/delete records
  - `admin`: Full control + user management + orthophoto management
