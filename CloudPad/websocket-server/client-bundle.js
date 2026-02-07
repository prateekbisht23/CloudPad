// client-bundle.js
import * as Y from 'yjs'
import { WebsocketProvider } from 'y-websocket'

// Expose to window for global access
window.Y = Y
window.WebsocketProvider = WebsocketProvider

console.log('Yjs Bundle Loaded', { Y, WebsocketProvider })
