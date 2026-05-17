'use client'

import React, { useState } from 'react'
import useSWR from 'swr'
import { 
  DollarSign, ArrowLeft, Receipt, 
  CheckCircle2, Clock, AlertCircle, 
  TrendingUp, Download, Filter
} from 'lucide-react'
import Link from 'next/link'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

interface Invoice {
  id: number
  name: string
  partner_id: [number, string]
  invoice_date: string
  amount_total: number
  payment_state: string
  state: string
}

export default function AccountingPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [currentTime, setCurrentTime] = useState<string | null>(null)

  React.useEffect(() => {
    setCurrentTime(new Date().toLocaleTimeString())
  }, [])

  const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
  
  const { data: dashboardData } = useSWR(`${apiBase}/api/dashboard`, fetcher)
  const { data: invoicesData, isLoading } = useSWR(`${apiBase}/api/accounting/invoices`, fetcher, {
    refreshInterval: 10000
  })

  const invoices: Invoice[] = invoicesData?.invoices || []

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground font-sans">
      <Sidebar 
        isOpen={sidebarOpen} 
        onToggle={() => setSidebarOpen(!sidebarOpen)} 
        onOpenModal={() => {}} 
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header 
          sidebarOpen={sidebarOpen} 
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} 
          onOpenModal={() => {}} 
        />
        
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="max-w-6xl mx-auto space-y-8">
            
            {/* Header Area */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <Link href="/" className="p-2 rounded-xl bg-muted hover:bg-muted/80 transition-colors">
                  <ArrowLeft className="w-5 h-5" />
                </Link>
                <div>
                  <h1 className="text-3xl font-bold tracking-tight text-gradient">Accounting Engine</h1>
                  <p className="text-muted-foreground text-sm">Real-time financial management & Odoo Sync</p>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="btn-secondary flex items-center gap-2">
                  <Download className="w-4 h-4" /> Export Report
                </button>
                <button className="btn-primary flex items-center gap-2">
                  <Receipt className="w-4 h-4" /> New Invoice
                </button>
              </div>
            </div>

            {/* Financial Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="card-gold p-6 bg-gold-500/5 border-gold-500/20 relative overflow-hidden group">
                <div className="absolute -right-4 -top-4 w-24 h-24 bg-gold-500/10 rounded-full blur-2xl group-hover:bg-gold-500/20 transition-all" />
                <p className="text-xs font-bold uppercase tracking-widest text-gold-400 mb-1">Weekly Revenue</p>
                <h3 className="text-3xl font-bold">{dashboardData?.revenue_week?.toLocaleString() || 0} <span className="text-sm font-normal text-muted-foreground">PKR</span></h3>
                <div className="mt-4 flex items-center gap-2 text-xs text-green-400">
                  <TrendingUp className="w-3 h-3" />
                  <span>+12% from last week</span>
                </div>
              </div>

              <div className="card-gold p-6 bg-blue-500/5 border-blue-500/20 relative overflow-hidden group">
                <p className="text-xs font-bold uppercase tracking-widest text-blue-400 mb-1">Paid Invoices</p>
                <h3 className="text-3xl font-bold">{dashboardData?.odoo_paid || 0}</h3>
                <div className="mt-4 flex items-center gap-2 text-xs text-blue-400">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>Collected successfully</span>
                </div>
              </div>

              <div className="card-gold p-6 bg-red-500/5 border-red-500/20 relative overflow-hidden group">
                <p className="text-xs font-bold uppercase tracking-widest text-red-400 mb-1">Pending Payments</p>
                <h3 className="text-3xl font-bold">{dashboardData?.odoo_pending_invoices || 0}</h3>
                <div className="mt-4 flex items-center gap-2 text-xs text-red-400">
                  <AlertCircle className="w-3 h-3" />
                  <span>Requires follow-up</span>
                </div>
              </div>
            </div>

            {/* Invoices Table */}
            <div className="card-gold p-0 overflow-hidden">
              <div className="p-6 border-b border-border flex items-center justify-between bg-muted/20">
                <h3 className="font-bold flex items-center gap-2">
                  <Receipt className="w-5 h-5 text-gold-400" />
                  Recent Invoices (Odoo Live)
                </h3>
                <div className="flex gap-2">
                   <div className="relative">
                      <Filter className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                      <select className="bg-background border border-border rounded-lg pl-9 pr-4 py-1.5 text-xs focus:ring-1 focus:ring-gold-500 outline-none appearance-none">
                        <option>All Status</option>
                        <option>Paid</option>
                        <option>Posted</option>
                      </select>
                   </div>
                </div>
              </div>

              <div className="overflow-x-auto">
                {isLoading ? (
                   <div className="p-12 text-center animate-pulse text-muted-foreground">Fetching Odoo ledger...</div>
                ) : (
                  <table className="w-full text-left text-sm">
                    <thead className="bg-muted/50 text-[10px] uppercase font-bold text-muted-foreground tracking-tighter">
                      <tr>
                        <th className="px-6 py-4">Invoice #</th>
                        <th className="px-6 py-4">Customer</th>
                        <th className="px-6 py-4">Date</th>
                        <th className="px-6 py-4">Amount</th>
                        <th className="px-6 py-4">Status</th>
                        <th className="px-6 py-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/50">
                      {invoices.length === 0 ? (
                        <tr><td colSpan={6} className="px-6 py-12 text-center text-muted-foreground italic">No invoices found in Odoo.</td></tr>
                      ) : (
                        invoices.map((inv) => (
                          <tr key={inv.id} className="hover:bg-muted/30 transition-colors group">
                            <td className="px-6 py-4 font-mono font-bold text-gold-400">{inv.name}</td>
                            <td className="px-6 py-4 font-medium">{inv.partner_id[1]}</td>
                            <td className="px-6 py-4 text-muted-foreground">{inv.invoice_date}</td>
                            <td className="px-6 py-4 font-bold">{inv.amount_total?.toLocaleString()} PKR</td>
                            <td className="px-6 py-4">
                              <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                                inv.payment_state === 'paid' 
                                  ? 'bg-green-500/10 text-green-400 border-green-500/20' 
                                  : 'bg-gold-500/10 text-gold-400 border-gold-500/20'
                              }`}>
                                {inv.payment_state.replace('_', ' ')}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-right">
                               <button className="text-xs font-bold text-muted-foreground hover:text-gold-400 transition-colors">View Details</button>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                )}
              </div>
              
              <div className="p-4 border-t border-border bg-muted/10 text-center">
                 <p className="text-[10px] text-muted-foreground uppercase tracking-widest">
                   System synced with Local Odoo (Docker) • Last update: {new Date().toLocaleTimeString()}
                 </p>
              </div>
            </div>

          </div>
        </main>
      </div>
    </div>
  )
}
