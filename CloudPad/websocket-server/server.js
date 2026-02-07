#!/usr/bin/env node

/**
 * CloudPad Yjs WebSocket Server
 * Provides real-time collaborative editing using Yjs CRDTs
 */

const WebSocket = require('ws')
const http = require('http')
const { setupWSConnection } = require('y-websocket/bin/utils')
require('dotenv').config()

const PORT = process.env.WS_PORT || 1234
const HOST = process.env.WS_HOST || 'localhost'

// Create HTTP server for health checks
const server = http.createServer((request, response) => {
    if (request.url === '/health') {
        response.writeHead(200, { 'Content-Type': 'application/json' })
        response.end(JSON.stringify({
            status: 'ok',
            activeConnections: wss.clients.size,
            uptime: process.uptime()
        }))
    } else {
        response.writeHead(200, { 'Content-Type': 'text/plain' })
        response.end('CloudPad Yjs WebSocket Server\n')
    }
})

// Create WebSocket server
const wss = new WebSocket.Server({
    server,
    // Allow connections from any origin in development
    // In production, restrict this to your domain
    verifyClient: (info) => {
        // Add CORS handling if needed
        return true
    }
})

// Track active documents for persistence
const activeDocuments = new Map()

wss.on('connection', (conn, req) => {
    const docName = req.url.slice(1) // Extract document name from URL

    console.log(`[${new Date().toISOString()}] New connection to document: ${docName}`)

    setupWSConnection(conn, req, {
        docName,
        gc: true // Enable garbage collection for efficiency
    })

    // Track document
    if (!activeDocuments.has(docName)) {
        activeDocuments.set(docName, {
            connections: 1,
            lastAccessed: Date.now()
        })
    } else {
        const doc = activeDocuments.get(docName)
        doc.connections++
        doc.lastAccessed = Date.now()
    }

    conn.on('close', () => {
        console.log(`[${new Date().toISOString()}] Connection closed for: ${docName}`)

        const doc = activeDocuments.get(docName)
        if (doc) {
            doc.connections--
            if (doc.connections === 0) {
                console.log(`[${new Date().toISOString()}] Last client disconnected from: ${docName}`)
                // Could trigger persistence here
                // For now, just keep the document in memory for 5 minutes
                setTimeout(() => {
                    if (doc.connections === 0) {
                        activeDocuments.delete(docName)
                        console.log(`[${new Date().toISOString()}] Document cleaned up: ${docName}`)
                    }
                }, 5 * 60 * 1000) // 5 minutes
            }
        }
    })
})

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM signal received: closing WebSocket server')
    wss.close(() => {
        server.close(() => {
            console.log('Server closed')
            process.exit(0)
        })
    })
})

process.on('SIGINT', () => {
    console.log('SIGINT signal received: closing WebSocket server')
    wss.close(() => {
        server.close(() => {
            console.log('Server closed')
            process.exit(0)
        })
    })
})

// Start server
server.listen(PORT, HOST, () => {
    console.log(`
╔═══════════════════════════════════════════════════════════════╗
║  CloudPad Yjs WebSocket Server                                ║
║  Real-time collaborative editing powered by Yjs               ║
║                                                               ║
║  Server running on: ws://${HOST}:${PORT}                     ║
║  Health check: http://${HOST}:${PORT}/health                 ║
╚═══════════════════════════════════════════════════════════════╝
`)
})

// Log active documents every minute
setInterval(() => {
    if (activeDocuments.size > 0) {
        console.log(`[${new Date().toISOString()}] Active documents:`)
        activeDocuments.forEach((info, docName) => {
            console.log(`  - ${docName}: ${info.connections} connection(s)`)
        })
    }
}, 60000)
