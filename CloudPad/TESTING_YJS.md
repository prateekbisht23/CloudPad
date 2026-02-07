# Testing Y js Real-Time Collaboration

## Quick Start

### 1. Start the WebSocket Server

```bash
cd websocket-server
node server.js
```

You should see:

```
╔═══════════════════════════════════════════════════════════════╗
║  CloudPad Yjs WebSocket Server                                ║
║  Real-time collaborative editing powered by Yjs               ║
║                                                               ║
║  Server running on: ws://localhost:1234                       ║
║  Health check: http://localhost:1234/health                   ║
╚═══════════════════════════════════════════════════════════════╝
```

### 2. Start Django Server

In a new terminal:

```bash
python3 manage.py runserver
```

### 3. Test Real-Time Collaboration

1. Open **http://localhost:8000** in Chrome
2. Enter a note ID (e.g., "collab-test")
3. Click "Create Pad"
4. Open the **same URL** in Firefox (or another Chrome window)
5. Type in one window - you should see it appear **instantly** in the other!

## Expected Behavior

### ✅ Status Indicators

- **"Connecting..."** (yellow) - Initial connection
- **"Connected"** (green) - WebSocket connected
- **"Syncing..."** (blue) - Content is being synced
- **"Saved"** (green) - Content is synced across all clients
- **"Disconnected"** (red) - Lost connection

### ✅ Real-Time Sync

- Type in one browser → appears instantly in another
- No 3-second delay like before
- Cursor position preserved when remote changes arrive
- Multiple users can edit simultaneously

### ✅ Conflict Resolution

- Two users type at the same time → both edits are merged automatically
- No "last write wins" - all edits are preserved
- Uses CRDTs (Conflict-free Replicated Data Types)

## Check Server Health

Visit: http://localhost:1234/health

Should return:

```json
{
  "status": "ok",
  "activeConnections": 2,
  "uptime": 123.45
}
```

## Console Logs

### Frontend (Browser Console)

```
[Yjs] Editor initialized for document: note-collab-test
[Yjs] Connection status: connected
[Yjs] Sync status: true
[CloudPad] Real-time editor ready
[CloudPad] Document synced
```

### Backend (WebSocket Server)

```
[2026-02-07T00:20:15.123Z] New connection to document: note-collab-test
[2026-02-07T00:20:45.456Z] Active documents:
  - note-collab-test: 2 connection(s)
```

## Troubleshooting

### Issue: "Connection Error" in status

**Solution:** Make sure WebSocket server is running on port 1234

```bash
lsof -i :1234  # Check if port is in use
```

### Issue: Changes not syncing

**Solution:** Check browser console for errors

- Make sure static files are collected: `python3 manage.py collectstatic`
- Verify YJS_WS_URL in .env: `YJS_WS_URL=ws://localhost:1234`

### Issue: Module not found error

**Solution:** The template uses ES6 modules from CDN

- Check network tab - should load from cdn.jsdelivr.net
- Make sure browser supports ES6 modules (all modern browsers do)

## Performance Testing

### Test with Multiple Users

1. Open 5-10 browser tabs with the same note
2. Type in different tabs
3. All should sync in real-time
4. Check WebSocket server logs for connection count

### Test Reconnection

1. Stop WebSocket server (`Ctrl+C`)
2. Status should show "Disconnected"
3. Restart server: `node server.js`
4. Should auto-reconnect and show "Connected"
5. Previous content should still be there

## Comparison: Before vs. After

### Before (Polling)

- ❌ 3-second delay between updates
- ❌ Status stuck on "Saved" even when typing
- ❌ High server load (constant polling)
- ❌ Conflicts possible (last write wins)

### After (Yjs WebSocket)

- ✅ Instant updates (<100ms)
- ✅ Status updates: Connecting → Connected → Syncing → Saved
- ✅ Low server load (push-based)
- ✅ Automatic conflict resolution

## Next Steps

Once verified working:

1. ✅ Real-time collaboration works
2. Deploy WebSocket server to production
3. Use `wss://` (WebSocket Secure) in production
4. Set up PM2 for process management
5. Configure nginx reverse proxy
6. Add user presence indicators (who's online)
