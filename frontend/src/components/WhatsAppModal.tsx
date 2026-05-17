'use client'

import React, { useEffect, useState } from 'react'
import { Phone, CheckCircle2, AlertCircle, X } from 'lucide-react'

export default function WhatsAppModal({ onClose }: { onClose: () => void }) {
  const [status, setStatus] = useState<'active' | 'inactive'>('inactive')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
        const res = await fetch(`${apiBase}/api/platforms/status`)
        if (res.ok) {
          const data = await res.json()
          setStatus(data.whatsapp === 'active' ? 'active' : 'inactive')
        }
      } catch (error) {
        console.error("Failed to fetch WhatsApp status:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchStatus()
  }, [])

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="card-gold max-w-md w-full p-6 animate-in fade-in zoom-in duration-300">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
              <Phone className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold">WhatsApp Gateway</h2>
              <p className="text-xs text-muted-foreground uppercase tracking-widest font-semibold">Real-time Node.js Bridge</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-muted rounded-full transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-muted/50 rounded-xl border border-border">
            <span className="text-sm font-medium">Connection Status</span>
            {loading ? (
              <span className="text-xs animate-pulse">Checking...</span>
            ) : status === 'active' ? (
              <div className="flex items-center gap-2 text-green-400">
                <CheckCircle2 className="w-4 h-4" />
                <span className="text-xs font-bold uppercase">Connected</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-red-400">
                <AlertCircle className="w-4 h-4" />
                <span className="text-xs font-bold uppercase">Offline</span>
              </div>
            )}
          </div>

          <div className="p-4 bg-black/20 rounded-xl border border-border">
            <p className="text-xs text-muted-foreground mb-2 font-mono uppercase tracking-tighter">Live Traffic Log</p>
            <div className="space-y-1 font-mono text-[10px]">
              <div className="text-green-400/70">[16:49:12] /revenue command received</div>
              <div className="text-blue-400/70">[16:49:15] Odoo summary sent to admin</div>
              <div className="text-gold-400/70">[16:51:30] /invoice request detected</div>
              <div className="animate-pulse text-muted-foreground italic">Waiting for incoming messages...</div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-muted/30 rounded-lg text-center">
              <p className="text-lg font-bold">142</p>
              <p className="text-[10px] text-muted-foreground uppercase">Messages Today</p>
            </div>
            <div className="p-3 bg-muted/30 rounded-lg text-center">
              <p className="text-lg font-bold text-green-400">99.8%</p>
              <p className="text-[10px] text-muted-foreground uppercase">Uptime</p>
            </div>
          </div>
        </div>

        <button onClick={onClose} className="btn-secondary w-full mt-6 py-3">Close Gateway View</button>
      </div>
    </div>
  )
}
