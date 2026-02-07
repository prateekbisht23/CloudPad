# CloudPad WebSocket Server

Node.js WebSocket server for real-time collaborative editing using Yjs.

## Installation

```bash
npm install
```

## Running

```bash
# Production
npm start

# Development (with auto-reload)
npm run dev
```

## Health Check

Visit `http://localhost:1234/health` to check server status.

## Configuration

Edit `.env` to configure:

- `WS_PORT` - WebSocket server port (default: 1234)
- `WS_HOST` - Host to bind to (default: 0.0.0.0)
- `DJANGO_API_URL` - Django backend URL for persistence

## How It Works

1. Clients connect to `ws://localhost:1234/{document-name}`
2. Yjs handles real-time synchronization automatically
3. Server tracks active connections per document
4. Documents are kept in memory while clients are connected
5. After last client disconnects, document is cleaned up after 5 minutes

## Production Deployment

For production:

1. Use a process manager like PM2: `pm2 start server.js`
2. Enable SSL: Use wss:// with a reverse proxy (nginx/caddy)
3. Set proper CORS origins in `server.js`
4. Configure firewall to allow WebSocket port
