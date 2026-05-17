'use client'

import React, { useEffect, useState } from 'react'
import { X, CheckCircle2, AlertCircle, Zap } from 'lucide-react'

export default function TwitterModal({ onClose }: { onClose: () => void }) {
  const [status, setStatus] = useState<'active' | 'inactive'>('inactive')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
        const res = await fetch(`${apiBase}/api/platforms/status`)
        if (res.ok) {
          const data = await res.json()
          setStatus(data.twitter === 'active' ? 'active' : 'inactive')
        }
      } catch (error) {
        console.error("Failed to fetch Twitter status:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchStatus()
  }, [])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-lg bg-card border border-border rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-300">
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${status === 'active' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'}`}>
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-xl font-bold">Twitter / X Integration</h3>
              <p className="text-sm text-muted-foreground">Manage your automated posts</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-muted rounded-full transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>
        <div className="p-6 space-y-4">
          <div className="p-4 bg-black/20 rounded-xl border border-border">
            <p className="text-xs text-muted-foreground mb-2 font-mono uppercase tracking-tighter">Real-time X Stream</p>
            <div className="space-y-2 font-mono text-[10px]">
              <div className="flex justify-between items-start text-blue-400/80">
                <span>[Scan] Tracking #K-Electric mentions...</span>
                <span className="text-[9px] text-muted-foreground">Just now</span>
              </div>
              <div className="flex justify-between items-start text-green-400/80">
                <span>[AI] Scheduled: Sustainability Report</span>
                <span className="text-[9px] text-muted-foreground">45m ago</span>
              </div>
              <div className="flex justify-between items-start text-muted-foreground">
                <span>[System] Trend detected: #SolarEnergy</span>
                <span className="text-[9px]">2h ago</span>
              </div>
              <div className="animate-pulse text-blue-400/50 italic">Listening to Twitter V2 Stream...</div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-muted/50 rounded-xl text-center">
              <p className="text-2xl font-bold text-blue-400">1.2k</p>
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Impressions Today</p>
            </div>
            <div className="p-4 bg-muted/50 rounded-xl text-center">
              <p className="text-2xl font-bold text-gold-400">42</p>
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Resolved DMs</p>
            </div>
          </div>
        </div>
        <div className="p-6 bg-muted/30 border-t border-border flex justify-end">
          <button onClick={onClose} className="btn-primary text-sm py-2 px-6 bg-foreground text-background rounded-lg hover:opacity-90">Close</button>
        </div>
      </div>
    </div>
  )
}
