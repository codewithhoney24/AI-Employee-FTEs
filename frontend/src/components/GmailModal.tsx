'use client'

import React, { useEffect, useState } from 'react'
import { Mail, CheckCircle2, AlertCircle, X } from 'lucide-react'

export default function GmailModal({ onClose }: { onClose: () => void }) {
  const [status, setStatus] = useState<'active' | 'inactive'>('inactive')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
        const res = await fetch(`${apiBase}/api/platforms/status`)
        if (res.ok) {
          const data = await res.json()
          setStatus(data.gmail === 'active' ? 'active' : 'inactive')
        }
      } catch (error) {
        console.error("Failed to fetch Gmail status:", error)
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
            <div className={`p-2 rounded-lg ${status === 'active' ? 'bg-red-500/20 text-red-400' : 'bg-gray-500/20 text-gray-400'}`}>
              <Mail className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Gmail</h2>
              <p className="text-xs text-muted-foreground uppercase tracking-widest font-semibold">Inbox AI Assistant</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-muted rounded-full transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-muted/50 rounded-xl border border-border">
            <span className="text-sm font-medium">Sync Status</span>
            {loading ? (
              <span className="text-xs animate-pulse">Checking...</span>
            ) : status === 'active' ? (
              <div className="flex items-center gap-2 text-green-400">
                <CheckCircle2 className="w-4 h-4" />
                <span className="text-xs font-bold uppercase">Active</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-red-400">
                <AlertCircle className="w-4 h-4" />
                <span className="text-xs font-bold uppercase">Paused</span>
              </div>
            )}
          </div>

          <div className="p-4 bg-red-500/10 rounded-xl border border-red-500/20">
            <p className="text-xs font-semibold text-red-400 uppercase mb-2">Recent AI Activity</p>
            <div className="space-y-2 text-[10px] text-muted-foreground">
              <div className="flex justify-between">
                <span>Drafted Reply: Solar Quote</span>
                <span className="text-foreground font-mono">2m ago</span>
              </div>
              <div className="flex justify-between">
                <span>Categorized: Support Ticket</span>
                <span className="text-foreground font-mono">15m ago</span>
              </div>
            </div>
          </div>
        </div>

        <button onClick={onClose} className="btn-secondary w-full mt-6 py-3">Close Gmail View</button>
      </div>
    </div>
  )
}
