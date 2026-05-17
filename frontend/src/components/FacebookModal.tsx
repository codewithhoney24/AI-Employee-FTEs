'use client'

import React, { useEffect, useState } from 'react'
import { Cloud, CheckCircle2, AlertCircle, X } from 'lucide-react'

export default function FacebookModal({ onClose }: { onClose: () => void }) {
  const [status, setStatus] = useState<'active' | 'inactive'>('inactive')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
        const res = await fetch(`${apiBase}/api/platforms/status`)
        if (res.ok) {
          const data = await res.json()
          setStatus(data.facebook === 'active' ? 'active' : 'inactive')
        }
      } catch (error) {
        console.error("Failed to fetch Facebook status:", error)
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
            <div className={`p-2 rounded-lg ${status === 'active' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'}`}>
              <Cloud className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Facebook</h2>
              <p className="text-xs text-muted-foreground uppercase tracking-widest font-semibold">Page Monitoring Active</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-muted rounded-full transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-muted/50 rounded-xl border border-border">
            <span className="text-sm font-medium">Page Connection</span>
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
                <span className="text-xs font-bold uppercase">Token Missing</span>
              </div>
            )}
          </div>

          <div className="p-4 bg-black/20 rounded-xl border border-border">
            <p className="text-xs text-muted-foreground mb-2 font-mono uppercase tracking-tighter">Live Monitoring Feed</p>
            <div className="space-y-2 font-mono text-[10px]">
              <div className="flex justify-between items-start text-blue-400/80">
                <span>[Scan] Checking recent posts...</span>
                <span className="text-[9px] text-muted-foreground">Just now</span>
              </div>
              <div className="flex justify-between items-start text-green-400/80">
                <span>[AI] Synced lead: Kamran Akmal to Odoo</span>
                <span className="text-[9px] text-muted-foreground">5m ago</span>
              </div>
              <div className="flex justify-between items-start text-muted-foreground">
                <span>[System] No new comments detected</span>
                <span className="text-[9px]">12m ago</span>
              </div>
              <div className="animate-pulse text-blue-400/50 italic">Monitoring Meta Graph API...</div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-muted/30 rounded-lg text-center border border-border">
              <p className="text-lg font-bold text-blue-500">1.4k</p>
              <p className="text-[10px] text-muted-foreground uppercase">Page Likes</p>
            </div>
            <div className="p-3 bg-muted/30 rounded-lg text-center border border-border">
              <p className="text-lg font-bold text-gold-400">3</p>
              <p className="text-[10px] text-muted-foreground uppercase">New Leads</p>
            </div>
          </div>
        </div>

        <button onClick={onClose} className="btn-secondary w-full mt-6 py-3">Close Facebook View</button>
      </div>
    </div>
  )
}
