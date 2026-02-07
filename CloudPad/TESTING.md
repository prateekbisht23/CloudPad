# Testing Guide for CloudPad

## Quick Start

### 1. Run the Development Server

```bash
cd /Users/prateekbisht/Desktop/CloudPad/CloudPad
python3 manage.py runserver
```

Visit: **http://localhost:8000**

---

## Manual Testing Checklist

### ✅ Home Page

- [ ] Navigate to http://localhost:8000
- [ ] Enter a custom URL ID (e.g., "test-note")
- [ ] Click "Create Pad" button
- [ ] Verify you're redirected to the note page

### ✅ Note Creation & Saving

- [ ] Type some content in the text area
- [ ] Wait 800ms - should see "Saved" status
- [ ] Check browser console (F12) - should see no errors
- [ ] Refresh the page - content should persist

### ✅ Input Validation

Test the validator security features:

**Valid URL IDs** (should work):

- `test-note`
- `my_note_123`
- `note-with-dashes`

**Invalid URL IDs** (should show error):

- `test--DROP` (SQL injection attempt)
- `<script>alert('xss')</script>` (XSS attempt)
- Special characters like `@#$%`

### ✅ File Upload

- [ ] Click the attachment icon
- [ ] Upload a PDF/image (under 10MB)
- [ ] Verify file appears in file list
- [ ] Download file - should work
- [ ] Delete file - should work

### ✅ Multi-Device Sync (Polling)

- [ ] Open same note URL in two browser windows
- [ ] Type in window 1
- [ ] Wait 3 seconds
- [ ] Window 2 should update automatically

### ✅ Error Handling

- [ ] Try to access invalid URL: `http://localhost:8000/test--DROP/`
- [ ] Should see user-friendly error page
- [ ] Check `logs/cloudpad.log` - should have warning logged

---

## Testing the Backend

### 1. Run Unit Tests

```bash
# Test the Note model
python3 manage.py test notes.tests.NoteModelTestCase -v 2

# Run all tests (when more are added)
python3 manage.py test
```

### 2. Test Management Command

```bash
# Dry run to see what would be deleted
python3 manage.py cleanup_expired_notes --dry-run

# See help/options
python3 manage.py cleanup_expired_notes --help
```

### 3. Check System Health

```bash
# Basic system check
python3 manage.py check

# Deployment readiness check
python3 manage.py check --deploy
```

---

## Testing Security Features

### ✅ CSRF Protection

1. Open browser DevTools → Network tab
2. Create a note
3. Look for POST request to `/your-note-id/save/`
4. Check Request Headers - should have `csrfmiddlewaretoken`

### ✅ Input Sanitization

1. Try entering HTML/JavaScript:
   ```html
   <script>alert('XSS')</script>
   <img src=x onerror=alert('XSS')>
   ```
2. Save and reload
3. Content should be plain text (no script execution)

### ✅ Logging

1. Make some requests (create notes, save, load)
2. Check log files:
   ```bash
   tail -f logs/cloudpad.log
   tail -f logs/errors.log
   ```
3. Look for structured log entries with timestamps

---

## Testing Auto-Deletion Feature

### Create Test Data

```bash
# Open Django shell
python3 manage.py shell
```

Then run this to create old test notes:

```python
from notes.models import Note
from django.utils import timezone
from datetime import timedelta

# Create a note that's 8 days old
old_note = Note.objects.create(url_id='old-test-note', content='This should expire')
old_note.last_accessed = timezone.now() - timedelta(days=8)
old_note.save()

# Create a fresh note (shouldn't expire)
fresh_note = Note.objects.create(url_id='fresh-note', content='This should stay')

print(f"Created old note: {old_note.url_id} (inactive for {old_note.get_inactive_days()} days)")
print(f"Created fresh note: {fresh_note.url_id} (inactive for {fresh_note.get_inactive_days()} days)")
```

Exit shell with `exit()`

### Test Cleanup

```bash
# See what would be deleted (dry run)
python3 manage.py cleanup_expired_notes --dry-run

# Actually delete expired notes
python3 manage.py cleanup_expired_notes

# Verify in shell
python3 manage.py shell
```

```python
from notes.models import Note

# Old note should be soft-deleted
old = Note.objects.get(url_id='old-test-note')
print(f"Old note is_deleted: {old.is_deleted}")  # Should be True

# Fresh note should still be active
fresh = Note.objects.get(url_id='fresh-note')
print(f"Fresh note is_deleted: {fresh.is_deleted}")  # Should be False
```

---

## Performance Testing

### Check Database Queries

Install Django Debug Toolbar (optional):

```bash
pip3 install django-debug-toolbar --user
```

Or check query count in shell:

```python
from django.db import connection
from notes.services import NoteService

# Reset query counter
connection.queries_executed = dict()

# Test operation
note, created = NoteService.get_or_create_note('performance-test')

# Check queries
from django.db import connection
print(f"Queries executed: {len(connection.queries)}")
```

---

## Verifying the Refactoring

### ✅ Service Layer Usage

Check that views use `NoteService`:

```bash
grep -n "NoteService" /Users/prateekbisht/Desktop/CloudPad/CloudPad/notes/views.py
```

Should see imports and method calls.

### ✅ Logging Works

```bash
# Make a request, then check logs:
grep "Note saved successfully" logs/cloudpad.log
grep "Note loaded successfully" logs/cloudpad.log
```

### ✅ Validators Active

```bash
# Check validators are imported:
grep -n "validators" /Users/prateekbisht/Desktop/CloudPad/CloudPad/notes/services.py
```

### ✅ Database Indexes

```bash
python3 manage.py dbshell
```

Then in PostgreSQL:

```sql
\d notes_note
-- Should see indexes on url_id, last_accessed, is_deleted
```

---

## Common Issues & Solutions

### Issue: Import errors

**Solution:** Make sure dependencies are installed:

```bash
pip3 install -r requirements.txt --user
```

### Issue: Database errors

**Solution:** Run migrations:

```bash
python3 manage.py migrate
```

### Issue: "Module not found: bleach"

**Solution:**

```bash
pip3 install bleach --user
```

### Issue: Can't access on port 8000

**Solution:** Try a different port:

```bash
python3 manage.py runserver 8001
```

---

## Next Steps After Testing

1. **Extract JavaScript** - Move inline JS to separate files
2. **Backend file uploads** - Move Supabase uploads to Django views
3. **Update README** - Remove false feature claims
4. **Add more tests** - Cover views and services
5. **Deploy** - Use the refactored, secure version

---

## Expected Results

After testing, you should see:

- ✅ All features working as before
- ✅ Better error messages for invalid input
- ✅ Logs being generated in `logs/` directory
- ✅ Auto-deletion working for old notes
- ✅ No security vulnerabilities in console
- ✅ Clean, organized codebase
