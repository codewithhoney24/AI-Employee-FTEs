'use client'

import React, { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import RevenueChart from '@/components/RevenueChart'
import Link from 'next/link'
import { DollarSign, TrendingUp, ArrowUpRight, ArrowDownRight, Filter, Download, ArrowLeft } from 'lucide-react'

export default function RevenuePage() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
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
          <div className="max-w-7xl mx-auto space-y-8">
            {/* Header section */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <Link 
                  href="/" 
                  className="p-2 rounded-xl bg-card border border-border hover:bg-muted transition-all hover:scale-110 shadow-sm"
                  title="Back to Dashboard"
                >
                  <ArrowLeft className="w-5 h-5 text-gold-400" />
                </Link>
                <div>
                  <h1 className="text-3xl font-bold text-gradient">Revenue Insights</h1>
                  <p className="text-muted-foreground mt-1">Detailed financial performance and forecasting for K-Electric.</p>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="btn-secondary flex items-center gap-2">
                  <Filter className="w-4 h-4" /> Filter Range
                </button>
                <button className="btn-primary flex items-center gap-2">
                  <Download className="w-4 h-4" /> Export Report
                </button>
              </div>
            </div>

            {/* Top metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard 
                label="Monthly Revenue" 
                value="PKR 4.2M" 
                trend="+15.2%" 
                positive={true} 
                icon={DollarSign}
                color="text-green-400"
              />
              <MetricCard 
                label="Average Invoice" 
                value="PKR 85,400" 
                trend="+2.4%" 
                positive={true} 
                icon={TrendingUp}
                color="text-blue-400"
              />
              <MetricCard 
                label="Outstanding" 
                value="PKR 1.1M" 
                trend="-8.1%" 
                positive={true} 
                icon={ArrowDownRight}
                color="text-gold-400"
              />
              <MetricCard 
                label="Projected" 
                value="PKR 5.8M" 
                trend="+22.5%" 
                positive={true} 
                icon={ArrowUpRight}
                color="text-purple-400"
              />
            </div>

            {/* Chart section */}
            <div className="card-gold p-6 min-h-[450px]">
              <div className="flex items-center justify-between mb-8">
                <h3 className="text-lg font-bold">Revenue Growth (Last 6 Months)</h3>
                <div className="flex gap-2 text-xs">
                  <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-muted border border-border">
                    <div className="w-2 h-2 rounded-full bg-gold-500" /> Actual
                  </span>
                  <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-muted border border-border">
                    <div className="w-2 h-2 rounded-full bg-muted-foreground/30" /> Projected
                  </span>
                </div>
              </div>
              <div className="h-[350px] w-full">
                <RevenueChart />
              </div>
            </div>

            {/* Detailed Table (Mock) */}
            <div className="card-gold overflow-hidden">
               <div className="p-6 border-b border-border">
                  <h3 className="text-lg font-bold">Recent Transactions</h3>
               </div>
               <div className="overflow-x-auto">
                 <table className="w-full text-sm text-left">
                    <thead className="bg-muted/50 text-muted-foreground uppercase text-[10px] tracking-wider">
                       <tr>
                          <th className="px-6 py-4">Transaction ID</th>
                          <th className="px-6 py-4">Client / Description</th>
                          <th className="px-6 py-4">Date</th>
                          <th className="px-6 py-4">Amount</th>
                          <th className="px-6 py-4">Status</th>
                       </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                       <tr className="hover:bg-muted/30">
                          <td className="px-6 py-4 font-mono text-xs">KE-TX-2984</td>
                          <td className="px-6 py-4 font-medium">Ali Khan (Solar Install)</td>
                          <td className="px-6 py-4 text-muted-foreground">May 4, 2026</td>
                          <td className="px-6 py-4 font-bold">PKR 125,000</td>
                          <td className="px-6 py-4"><span className="badge-gold bg-green-500/10 text-green-400">Paid</span></td>
                       </tr>
                       <tr className="hover:bg-muted/30">
                          <td className="px-6 py-4 font-mono text-xs">KE-TX-2985</td>
                          <td className="px-6 py-4 font-medium">XYZ Company (Maintenance)</td>
                          <td className="px-6 py-4 text-muted-foreground">May 3, 2026</td>
                          <td className="px-6 py-4 font-bold">PKR 75,000</td>
                          <td className="px-6 py-4"><span className="badge-gold bg-gold-500/10 text-gold-400">Pending</span></td>
                       </tr>
                    </tbody>
                 </table>
               </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

function MetricCard({ label, value, trend, positive, icon: Icon, color }: any) {
  return (
    <div className="card-gold p-6 bg-muted/5">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-2 rounded-lg bg-muted border border-border ${color}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div className={`flex items-center gap-1 text-xs font-bold ${positive ? 'text-green-400' : 'text-red-400'}`}>
          {trend} {positive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
        </div>
      </div>
      <p className="text-sm text-muted-foreground uppercase tracking-wider font-medium">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  )
}
