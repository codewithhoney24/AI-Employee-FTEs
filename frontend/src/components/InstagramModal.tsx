'use client'

import React, { useEffect, useState } from 'react'
import { Camera, CheckCircle2, AlertCircle, X } from 'lucide-react'

export default function InstagramModal({ onClose }: { onClose: () => void }) {
  const [status, setStatus] = useState<'active' | 'inactive'>('inactive')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
        const res = await fetch(`${apiBase}/api/platforms/status`)
        if (res.ok) {
          const data = await res.json()
          setStatus(data.instagram === 'active' ? 'active' : 'inactive')
        }
      } catch (error) {
        console.error("Failed to fetch Instagram status:", error)
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
            <div className={`p-2 rounded-lg ${status === 'active' ? 'bg-pink-500/20 text-pink-400' : 'bg-red-500/20 text-red-400'}`}>
              <Camera className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Instagram</h2>
              <p className="text-xs text-muted-foreground uppercase tracking-widest font-semibold">Visual Commerce Engine</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-muted rounded-full transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-muted/50 rounded-xl border border-border">
            <span className="text-sm font-medium">Business Account</span>
            {loading ? (
              <span className="text-xs animate-pulse">Checking...</span>
            ) : status === 'active' ? (
              <div className="flex items-center gap-2 text-green-400">
                <CheckCircle2 className="w-4 h-4" />
                <span className="text-xs font-bold uppercase">Linked</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-red-400">
                <AlertCircle className="w-4 h-4" />
                <span className="text-xs font-bold uppercase">Not Found</span>
              </div>
            )}
          </div>

          <div className="p-4 bg-black/20 rounded-xl border border-border">
            <p className="text-xs text-muted-foreground mb-2 font-mono uppercase tracking-tighter">Live Monitoring</p>
            <div className="space-y-2 font-mono text-[10px]">
              <div className="flex justify-between items-start text-pink-400/80">
                <span>[Scan] Analyzing visual sentiment...</span>
                <span className="text-[9px] text-muted-foreground">Just now</span>
              </div>
              <div className="flex justify-between items-start text-green-400/80">
                <span>[AI] New inquiry from @ali_k h8</span>
                <span className="text-[9px] text-muted-foreground">12m ago</span>
              </div>
              <div className="flex justify-between items-start text-muted-foreground">
                <span>[System] Story reach increased by 12%</span>
                <span className="text-[9px]">1h ago</span>
              </div>
              <div className="animate-pulse text-pink-400/50 italic">Monitoring Instagram Business API...</div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-muted/30 rounded-lg text-center border border-border">
              <p className="text-lg font-bold text-pink-500">1.2k</p>
              <p className="text-[10px] text-muted-foreground uppercase">Reach</p>
            </div>
            <div className="p-3 bg-muted/30 rounded-lg text-center border border-border">
              <p className="text-lg font-bold text-gold-400">85%</p>
              <p className="text-[10px] text-muted-foreground uppercase">Sentiment</p>
            </div>
          </div>
        </div>

        <button onClick={onClose} className="btn-secondary w-full mt-6 py-3">Close Instagram View</button>
      </div>
    </div>
  )
}

