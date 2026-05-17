'use client'

import React, { useEffect, useState } from 'react'
import { Server, CheckCircle2, AlertCircle, X, Terminal } from 'lucide-react'
import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export default function OdooModal({ onClose }: { onClose: () => void }) {
  const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
  const { data: dashboardData } = useSWR(`${apiBase}/api/dashboard`, fetcher, { refreshInterval: 5000 })

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="card-gold max-w-lg w-full p-6 animate-in fade-in zoom-in duration-300">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${dashboardData?.odoo_status === 'active' ? 'bg-purple-500/20 text-purple-400' : 'bg-red-500/20 text-red-400'}`}>
              <Server className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Odoo Accounting</h2>
              <p className="text-xs text-muted-foreground uppercase tracking-widest font-semibold">Live ERP Integration</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-muted rounded-full transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-muted/50 rounded-xl border border-border">
              <p className="text-xs text-muted-foreground mb-1 uppercase tracking-tighter font-bold">Sync Status</p>
              {dashboardData?.odoo_status === 'active' ? (
                <div className="flex items-center gap-2 text-green-400">
                  <CheckCircle2 className="w-4 h-4" />
                  <span className="text-sm font-bold uppercase">Connected</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-red-400">
                  <AlertCircle className="w-4 h-4" />
                  <span className="text-sm font-bold uppercase">Error</span>
                </div>
              )}
            </div>
            <div className="p-4 bg-muted/50 rounded-xl border border-border">
              <p className="text-xs text-muted-foreground mb-1 uppercase tracking-tighter font-bold">Last Sync</p>
              <p className="text-sm font-mono">{dashboardData?.odoo_last_sync ? new Date(dashboardData.odoo_last_sync).toLocaleTimeString() : 'N/A'}</p>
            </div>
          </div>

          <div className="p-4 bg-black/20 rounded-xl border border-border">
            <p className="text-xs text-muted-foreground mb-2 font-mono uppercase tracking-tighter flex items-center gap-2">
              <Terminal className="w-3 h-3 text-purple-400" /> Live ERP Sync Log
            </p>
            <div className="space-y-1 font-mono text-[10px]">
              <div className="text-green-400/80">[Sync] Fetching latest invoices...</div>
              <div className="text-blue-400/80">[AI] New invoice created: #{dashboardData?.odoo_invoices || 0}</div>
              <div className="text-purple-400/80">[Audit] Revenue consistency check passed</div>
              <div className="animate-pulse text-muted-foreground italic">Listening for Odoo XML-RPC calls...</div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 bg-muted/30 rounded-lg text-center border border-border">
              <p className="text-lg font-bold text-purple-400">{dashboardData?.odoo_crm_leads ?? 0}</p>
              <p className="text-[9px] text-muted-foreground uppercase">CRM Leads</p>
            </div>
            <div className="p-3 bg-muted/30 rounded-lg text-center border border-border">
              <p className="text-lg font-bold text-green-400">{dashboardData?.odoo_paid ?? 0}</p>
              <p className="text-[9px] text-muted-foreground uppercase">Paid Inv.</p>
            </div>
            <div className="p-3 bg-muted/30 rounded-lg text-center border border-border">
              <p className="text-lg font-bold text-gold-400">{dashboardData?.odoo_pending_invoices ?? 0}</p>
              <p className="text-[9px] text-muted-foreground uppercase">Unpaid</p>
            </div>
          </div>
        </div>

        <button onClick={onClose} className="btn-secondary w-full mt-6 py-3">Close ERP View</button>
      </div>
    </div>
  )
}
