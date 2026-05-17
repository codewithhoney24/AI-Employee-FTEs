'use client'

import React, { useState, useEffect, useCallback, useRef } from 'react'
import {
  Bell,
  User,
  Circle,
  Settings,
  Trash2,
  CheckCheck,
  ArrowLeft,
  Clock,
  Filter,
  X,
  RefreshCw,
} from 'lucide-react'
import { Notification, ModalType } from '@/types'

/* ================= TYPES ================= */

interface Activity {
  action?: string
  details?: Record<string, unknown>
  category?: string
  timestamp: string
}

interface NotificationsPanelProps {
  onBack?: () => void
  onSync?: (notifs: Notification[]) => void
  onOpenModal?: (type: ModalType) => void
}

/* ================= CONFIG ================= */

const typeConfig = {
  lead: { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-l-blue-500', icon: User },
  payment: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-l-green-500', icon: Circle },
  task: { bg: 'bg-purple-500/20', text: 'text-purple-400', border: 'border-l-purple-500', icon: Settings },
  alert: { bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-l-orange-500', icon: Bell },
  social: { bg: 'bg-pink-500/20', text: 'text-pink-400', border: 'border-l-pink-500', icon: Bell },
} as const

/* ================= HELPERS ================= */

function formatTimeAgo(timestamp: string): string {
  if (!timestamp) return 'Unknown'

  const now = new Date()
  const then = new Date(timestamp)
  const diffMs = now.getTime() - then.getTime()

  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} min ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
}

/* ================= MAPPER ================= */

function activityToNotification(activity: Activity & { id?: string }, index: number): Notification {
  const typeMap: Record<string, Notification['type']> = {
    lead_detected: 'lead',
    post_published: 'social',
    comment_replied: 'social',
    task_completed: 'task',
    approval_approved: 'payment',
    approval_rejected: 'alert',
    error: 'alert',
  }

  const title =
    activity.action
      ? activity.action.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
      : 'Activity'

  const desc =
    activity.details
      ? JSON.stringify(activity.details).slice(0, 100)
      : activity.category || ''

  return {
    id: activity.id || String(index + 1),
    title,
    desc,
    time: formatTimeAgo(activity.timestamp),
    read: false,
    type: typeMap[activity.action || ''] || 'task',
    action: 'View',
  }
}

/* ================= FALLBACK DATA ================= */

const fallbackNotifications: Notification[] = [
  { id: '1', title: 'New Facebook Lead', desc: 'John Smith commented...', time: '2 min ago', read: false, type: 'lead', action: 'View Lead' },
  { id: '2', title: 'Payment Approved', desc: 'Invoice #1024...', time: '15 min ago', read: false, type: 'payment', action: 'View Invoice' },
]

/* ================= COMPONENT ================= */

export default function NotificationsPanel({
  onBack,
  onSync,
  onOpenModal,
}: NotificationsPanelProps) {

  const [notifs, setNotifs] = useState<Notification[]>(fallbackNotifications)
  const [filter, setFilter] = useState<'all' | 'unread'>('all')
  const [showFilterDropdown, setShowFilterDropdown] = useState(false)
  const [loading, setLoading] = useState(false)
  const [connected, setConnected] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  const wsRef = useRef<WebSocket | null>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const connectWebSocketRef = useRef<(() => void) | null>(null)

  const unreadCount = notifs.filter(n => !n.read).length
  const filteredNotifs = filter === 'unread' ? notifs.filter(n => !n.read) : notifs

  /* ================= ACTIONS ================= */

  const markRead = (id: string) => {
    setNotifs(prev => prev.map(n => n.id === id ? { ...n, read: true } : n))
  }

  const markAllRead = () => {
    setNotifs(prev => prev.map(n => ({ ...n, read: true })))
  }

  const deleteNotif = (id: string) => {
    setNotifs(prev => prev.filter(n => n.id !== id))
  }

  const clearAll = () => {
    setNotifs([])
  }

  const handleAction = (notif: Notification) => {
    markRead(notif.id)
    if (notif.type === 'lead' || notif.type === 'social') {
      onOpenModal?.('facebook')
    } else if (notif.type === 'payment') {
      onOpenModal?.('odoo')
    }
  }

  /* ================= FETCH ================= */

  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true)
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
      const res = await fetch(`${apiBase}/api/activity?hours=24`)
      if (!res.ok) throw new Error('Failed to fetch')

      const data = await res.json()
      const mapped: Notification[] = (data.activity || []).map(
        (a: Activity, i: number) => activityToNotification(a, i)
      )

      setNotifs(prev => {
        const existing = new Set(prev.map(n => n.title + n.desc))
        const fresh = mapped.filter(n => !existing.has(n.title + n.desc))
        return [...fresh, ...prev].slice(0, 50)
      })

      setConnected(true)
    } catch {
      setConnected(false)
    } finally {
      setLoading(false)
      setLastUpdate(new Date())
    }
  }, [])

  /* ================= WEBSOCKET ================= */

  const connectWebSocket = useCallback(() => {
    try {
      if (wsRef.current?.readyState === WebSocket.OPEN) return

      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
      const wsUrl = apiBase.replace('http', 'ws') + '/ws'
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => setConnected(true)

      ws.onmessage = (event: MessageEvent) => {
        try {
          const msg = JSON.parse(event.data)
          const newNotif: Notification = {
            id: String(Date.now()),
            title: msg.type === 'approval_updated' ? 'Approval Updated' : 'System Update',
            desc: msg.action || 'Update received',
            time: 'Just now',
            read: false,
            type: 'alert',
            action: 'View',
          }
          setNotifs(prev => [newNotif, ...prev].slice(0, 50))
        } catch { /* ignore */ }
      }

      ws.onclose = () => {
        setConnected(false)
        setTimeout(() => connectWebSocketRef.current?.(), 5000)
      }

      ws.onerror = () => setConnected(false)
    } catch {
      setConnected(false)
    }
  }, [])

  // Sync ref with callback
  useEffect(() => {
    connectWebSocketRef.current = connectWebSocket
  }, [connectWebSocket])

  /* ================= POLLING ================= */

  const startPolling = useCallback(() => {
    if (pollRef.current) clearInterval(pollRef.current)
    pollRef.current = setInterval(fetchNotifications, 30000)
  }, [fetchNotifications])

  /* ================= INIT ================= */

  useEffect(() => {
    // Wrap in a non-render-blocking way to satisfy strict linting
    const init = async () => {
      await fetchNotifications()
      connectWebSocket()
      startPolling()
    }
    init()

    return () => {
      wsRef.current?.close()
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [fetchNotifications, connectWebSocket, startPolling])

  /* ================= SYNC ================= */

  // Use a ref to track the last synced notifications to avoid redundant calls
  const lastSyncedRef = useRef<string>('')

  useEffect(() => {
    const notifsJson = JSON.stringify(notifs)
    if (onSync && notifsJson !== lastSyncedRef.current) {
      onSync(notifs)
      lastSyncedRef.current = notifsJson
    }
  }, [notifs, onSync])

  /* ================= UI ================= */

  return (
    <div className="fixed inset-0 z-50 bg-background flex flex-col animate-in fade-in slide-in-from-right duration-300">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10 bg-black/40 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <button 
            onClick={onBack}
            className="p-2 hover:bg-white/10 rounded-full transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-xl font-bold flex items-center gap-2">
              Notifications
              {unreadCount > 0 && (
                <span className="px-2 py-0.5 text-xs bg-primary text-primary-foreground rounded-full">
                  {unreadCount}
                </span>
              )}
            </h1>
            <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
              <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
              {connected ? 'Live Connected' : 'Offline'}
              <span className="mx-1">•</span>
              <Clock className="w-3 h-3" />
              Updated {lastUpdate.toLocaleTimeString()}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchNotifications}
            disabled={loading}
            className={`p-2 hover:bg-white/10 rounded-lg transition-colors ${loading ? 'animate-spin' : ''}`}
            title="Refresh"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
          <div className="relative">
            <button
              onClick={() => setShowFilterDropdown(!showFilterDropdown)}
              className={`p-2 hover:bg-white/10 rounded-lg transition-colors ${filter !== 'all' ? 'text-primary' : ''}`}
            >
              <Filter className="w-5 h-5" />
            </button>
            {showFilterDropdown && (
              <div className="absolute right-0 mt-2 w-40 bg-card border border-white/10 rounded-xl shadow-2xl z-10 overflow-hidden">
                <button
                  onClick={() => { setFilter('all'); setShowFilterDropdown(false); }}
                  className={`w-full text-left px-4 py-2 hover:bg-white/5 text-sm ${filter === 'all' ? 'text-primary bg-primary/10' : ''}`}
                >
                  All Notifications
                </button>
                <button
                  onClick={() => { setFilter('unread'); setShowFilterDropdown(false); }}
                  className={`w-full text-left px-4 py-2 hover:bg-white/5 text-sm ${filter === 'unread' ? 'text-primary bg-primary/10' : ''}`}
                >
                  Unread Only
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-white/10 bg-black/20 text-xs">
        <div className="flex gap-4">
          <button onClick={markAllRead} className="flex items-center gap-1.5 hover:text-primary transition-colors">
            <CheckCheck className="w-3.5 h-3.5" />
            Mark all read
          </button>
        </div>
        <button onClick={clearAll} className="flex items-center gap-1.5 hover:text-destructive transition-colors text-muted-foreground">
          <Trash2 className="w-3.5 h-3.5" />
          Clear all
        </button>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
        {filteredNotifs.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-muted-foreground opacity-50">
            <Bell className="w-16 h-16 mb-4" />
            <p className="text-lg">No notifications yet</p>
          </div>
        ) : (
          filteredNotifs.map((n) => {
            const config = typeConfig[n.type]
            const Icon = config.icon
            return (
              <div
                key={n.id}
                className={`group relative flex gap-4 p-4 rounded-2xl border transition-all duration-300 hover:scale-[1.01] ${
                  n.read ? 'bg-white/[0.02] border-white/5' : `bg-white/[0.05] border-white/10 ${config.border} border-l-4 shadow-lg shadow-black/20`
                }`}
              >
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${config.bg} ${config.text}`}>
                  <Icon className="w-6 h-6" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className={`font-semibold truncate ${n.read ? 'text-muted-foreground' : 'text-white'}`}>
                      {n.title}
                    </h3>
                    <span className="text-[10px] text-muted-foreground whitespace-nowrap mt-1 uppercase tracking-wider">
                      {n.time}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1 line-clamp-2 leading-relaxed">
                    {n.desc}
                  </p>
                  
                  <div className="flex items-center gap-3 mt-3">
                    {n.action && (
                      <button 
                        onClick={() => handleAction(n)}
                        className="text-xs font-medium text-primary hover:underline"
                      >
                        {n.action}
                      </button>
                    )}
                    {!n.read && (
                      <button 
                        onClick={() => markRead(n.id)}
                        className="text-[10px] font-bold text-green-500 uppercase tracking-widest hover:bg-green-500/10 px-2 py-0.5 rounded"
                      >
                        Mark as read
                      </button>
                    )}
                  </div>
                </div>

                <button
                  onClick={() => deleteNotif(n.id)}
                  className="absolute top-4 right-4 p-2 opacity-0 group-hover:opacity-100 transition-opacity hover:text-destructive"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
