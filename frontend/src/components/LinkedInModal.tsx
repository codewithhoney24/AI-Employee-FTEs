'use client'

import React, { useEffect, useState } from 'react'
import { X, CheckCircle2, AlertCircle } from 'lucide-react'

export default function LinkedInModal({ onClose }: { onClose: () => void }) {
  const [status, setStatus] = useState<'active' | 'inactive'>('inactive')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
        const res = await fetch(`${apiBase}/api/platforms/status`)
        if (res.ok) {
          const data = await res.json()
          setStatus(data.linkedin === 'active' ? 'active' : 'inactive')
        }
      } catch (error) {
        console.error("Failed to fetch LinkedIn status:", error)
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
            <div className="w-10 h-10 rounded-full bg-blue-700/20 flex items-center justify-center text-blue-500">
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
              </svg>
            </div>
            <div>
              <h3 className="text-xl font-bold">LinkedIn Integration</h3>
              <p className="text-sm text-muted-foreground">Professional B2B Automation</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-muted rounded-full transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>
        <div className="p-6 space-y-4">
          <div className="flex items-center gap-4 p-4 bg-muted/50 rounded-xl border border-border">
            <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-xl">
              D
            </div>
            <div>
              <p className="font-bold">Digital Dreamers</p>
              <p className="text-xs text-muted-foreground">Development Specialist at Freelance | Self-Employed</p>
              <div className="flex items-center gap-2 mt-1">
                {loading ? (
                  <span className="text-[10px] animate-pulse">Checking status...</span>
                ) : status === 'active' ? (
                  <>
                    <span className="w-2 h-2 rounded-full bg-green-500" />
                    <span className="text-[10px] text-green-400 font-medium uppercase tracking-wider">Connected</span>
                  </>
                ) : (
                  <>
                    <span className="w-2 h-2 rounded-full bg-red-500" />
                    <span className="text-[10px] text-red-400 font-medium uppercase tracking-wider">Disconnected</span>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="p-4 bg-black/20 rounded-xl border border-border">
            <p className="text-xs text-muted-foreground mb-2 font-mono uppercase tracking-tighter">Live Network Feed</p>
            <div className="space-y-2 font-mono text-[10px]">
              <div className="flex justify-between items-start text-blue-400/80">
                <span>[Scan] Checking B2B engagement...</span>
                <span className="text-[9px] text-muted-foreground">Just now</span>
              </div>
              <div className="flex justify-between items-start text-green-400/80">
                <span>[AI] Professional reply sent to T. Malik</span>
                <span className="text-[9px] text-muted-foreground">18m ago</span>
              </div>
              <div className="flex justify-between items-start text-muted-foreground">
                <span>[System] New connection request accepted</span>
                <span className="text-[9px]">4h ago</span>
              </div>
              <div className="animate-pulse text-blue-400/50 italic">Monitoring LinkedIn V2 API...</div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-muted/50 rounded-xl text-center border border-border hover:border-blue-500/30 transition-colors">
              <p className="text-2xl font-bold text-blue-500">842</p>
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">Post Reach</p>
            </div>
            <div className="p-4 bg-muted/50 rounded-xl text-center border border-border hover:border-gold-500/30 transition-colors">
              <p className="text-2xl font-bold text-gold-400">12</p>
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold">B2B Inquiries</p>
            </div>
          </div>
        </div>
        <div className="p-6 bg-muted/30 border-t border-border flex justify-end">
          <button onClick={onClose} className="btn-primary text-sm py-2 px-6 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">Close</button>
        </div>
      </div>
    </div>
  )
}
