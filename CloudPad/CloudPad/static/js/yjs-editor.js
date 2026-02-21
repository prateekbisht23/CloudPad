/**
 * CloudPad Yjs Real-Time Collaboration
 * Replaces polling-based sync with WebSocket-powered real-time editing
 */

// Uses global window.Y from local bundle
// Bundle source: websocket-server/client-bundle.js

export class YjsEditor {
    constructor(config) {
        this.config = {
            wsUrl: config.wsUrl || 'ws://localhost:1234',
            documentName: config.documentName,
            textarea: config.textarea,
            statusElement: config.statusElement,
            onReady: config.onReady || (() => { }),
            onSync: config.onSync || (() => { }),
            onError: config.onError || ((err) => console.error('Yjs error:', err))
        }

        this.ydoc = null
        this.provider = null
        this.yText = null
        this.awareness = null
        this.isInitialized = false

        this.init()
    }

    init() {
        try {
            // Check globals
            if (typeof window.Y === 'undefined' || typeof window.WebsocketProvider === 'undefined') {
                throw new Error('Yjs libraries not loaded. Check yjs-bundle.js')
            }

            const Y = window.Y
            const WebsocketProvider = window.WebsocketProvider

            // Create Yjs document
            this.ydoc = new Y.Doc()

            // Connect to WebSocket server
            this.provider = new WebsocketProvider(
                this.config.wsUrl,
                this.config.documentName,
                this.ydoc,
                {
                    connect: true
                }
            )

            // Get shared text type
            this.yText = this.ydoc.getText('content')

            // Get awareness for presence
            this.awareness = this.provider.awareness

            // Bind events
            this.bindEvents()

            // Bind textarea
            this.bindTextarea()

            console.log('[Yjs] Editor initialized for document:', this.config.documentName)

        } catch (error) {
            this.config.onError(error)
            throw error
        }
    }

    bindEvents() {
        // Track whether we've ever had a connection error (cleared on reconnect)
        this._hadConnectionError = false

        // Connection status
        this.provider.on('status', ({ status }) => {
            console.log('[Yjs] Connection status:', status)

            if (this.config.statusElement) {
                if (status === 'connected') {
                    // Clear any previous connection error
                    this._hadConnectionError = false
                    this.config.statusElement.innerText = 'Connected'
                    this.config.statusElement.className = 'text-green-600'
                } else if (status === 'disconnected') {
                    // Only show Disconnected if we haven't already shown a connection error
                    if (!this._hadConnectionError) {
                        this.config.statusElement.innerText = 'Disconnected'
                        this.config.statusElement.className = 'text-orange-500'
                    }
                } else if (status === 'connecting') {
                    this._hadConnectionError = false
                    this.config.statusElement.innerText = 'Connecting...'
                    this.config.statusElement.className = 'text-yellow-600'
                }
            }
        })

        // Sync status
        this.provider.on('sync', (isSynced) => {
            console.log('[Yjs] Sync status:', isSynced)

            if (isSynced) {
                // Bootstrap content from server-rendered HTML if Yjs doc is empty
                // This prevents duplication on reload (race condition)
                if (this.yText.length === 0 && this.config.textarea.value) {
                    console.log('[Yjs] Bootstrapping content from server')
                    this.yText.insert(0, this.config.textarea.value)
                }

                if (!this.isInitialized) {
                    this.isInitialized = true
                    this.config.onReady()
                }

                // Synced — clear any lingering error state
                this._hadConnectionError = false
            }

            if (this.config.statusElement && isSynced) {
                this.config.statusElement.innerText = 'Saved'
                this.config.statusElement.className = 'text-green-600'
            } else if (this.config.statusElement && !this._hadConnectionError) {
                this.config.statusElement.innerText = 'Syncing...'
                this.config.statusElement.className = 'text-blue-600'
            }

            this.config.onSync(isSynced)
        })

        // Connection errors — mark the flag but don't permanently lock the UI
        this.provider.on('connection-error', (error) => {
            console.error('[Yjs] Connection error:', error)
            this._hadConnectionError = true
            this.config.onError(error)

            if (this.config.statusElement) {
                this.config.statusElement.innerText = 'Reconnecting...'
                this.config.statusElement.className = 'text-yellow-600'
            }

            // Auto-clear the error message after 4 seconds if the provider reconnects
            clearTimeout(this._errorClearTimeout)
            this._errorClearTimeout = setTimeout(() => {
                if (this.provider.wsconnected) {
                    this._hadConnectionError = false
                    if (this.config.statusElement) {
                        this.config.statusElement.innerText = 'Saved'
                        this.config.statusElement.className = 'text-green-600'
                    }
                } else if (this.config.statusElement) {
                    this.config.statusElement.innerText = 'Offline'
                    this.config.statusElement.className = 'text-gray-500'
                }
            }, 4000)
        })
    }

    bindTextarea() {
        const textarea = this.config.textarea

        if (!textarea) {
            throw new Error('Textarea element is required')
        }

        let isLocalChange = false

        // Update Yjs when textarea changes
        textarea.addEventListener('input', () => {
            if (!isLocalChange) {
                const value = textarea.value

                // Replace entire text content
                this.ydoc.transact(() => {
                    this.yText.delete(0, this.yText.length)
                    this.yText.insert(0, value)
                })

                // Update status
                if (this.config.statusElement) {
                    this.config.statusElement.innerText = 'Syncing...'
                    this.config.statusElement.className = 'text-blue-600'

                    // Reset to Saved after delay (optimistic UI)
                    clearTimeout(this.saveTimeout)
                    this.saveTimeout = setTimeout(() => {
                        // Always persist to Django backend regardless of WS state
                        this.saveToBackend(this.ydoc.getText('content').toString())

                        if (this.provider.wsconnected) {
                            this.config.statusElement.innerText = 'Saved'
                            this.config.statusElement.className = 'text-green-600'
                        } else {
                            // Saved to DB even if real-time WS is down
                            this.config.statusElement.innerText = 'Saved'
                            this.config.statusElement.className = 'text-green-600'
                        }
                    }, 1000)
                }
            }
        })

        // Update textarea when Yjs changes (from other clients)
        this.yText.observe((event) => {
            // Fix: Applied changes if origin is the provider (remote) OR if it's null (unspecified) 
            if (event.transaction.origin === this.provider) {
                // Change came from another client
                isLocalChange = true

                // Preserve cursor position
                const selectionStart = textarea.selectionStart
                const selectionEnd = textarea.selectionEnd
                const oldLength = textarea.value.length

                // Update text
                textarea.value = this.yText.toString()

                // Restore cursor position (adjusted for length change)
                const lengthDiff = textarea.value.length - oldLength
                textarea.selectionStart = Math.min(selectionStart + lengthDiff, textarea.value.length)
                textarea.selectionEnd = Math.min(selectionEnd + lengthDiff, textarea.value.length)

                isLocalChange = false

                // Also trigger save on remote changes to keep DB consistent
                clearTimeout(this.saveTimeout)
                this.saveTimeout = setTimeout(() => {
                    this.saveToBackend(this.yText.toString())
                }, 2000)
            }
        })

    }

    /**
     * Get current content as string
     */
    getContent() {
        return this.yText.toString()
    }

    /**
     * Set content (use sparingly, prefer letting Yjs handle updates)
     */
    setContent(content) {
        this.ydoc.transact(() => {
            this.yText.delete(0, this.yText.length)
            this.yText.insert(0, content)
        })
    }

    /**
     * Get number of connected users
     */
    getConnectedUsers() {
        return this.awareness.getStates().size
    }

    /**
     * Persist content to Django backend
     */
    saveToBackend(content) {
        // Need to get CSRF token from cookie or DOM
        const getCookie = (name) => {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        const csrftoken = getCookie('csrftoken');
        const urlId = this.config.documentName;

        fetch(`/${urlId}/save/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ content: content })
        })
            .then(response => response.json())
            .then(data => {
                console.log('[Yjs] Saved to backend:', data.status)
            })
            .catch(error => {
                console.error('[Yjs] Backend save failed:', error)
            })
    }

    /**
     * Clean up and disconnect
     */
    destroy() {
        if (this.provider) {
            this.provider.disconnect()
            this.provider.destroy()
        }
        if (this.ydoc) {
            this.ydoc.destroy()
        }
        console.log('[Yjs] Editor destroyed')
    }
}

// Export for use in templates
window.YjsEditor = YjsEditor
