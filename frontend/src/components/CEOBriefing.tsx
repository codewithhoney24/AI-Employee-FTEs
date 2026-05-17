'use client'

import React, { useState } from 'react'
import { 
  TrendingUp, AlertCircle, CheckCircle2, 
  ArrowRight, Download, Sparkles, 
  DollarSign, Users, Target, Zap, ArrowLeft 
} from 'lucide-react'
import Link from 'next/link'
import useSWR, { mutate } from 'swr'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export default function CEOBriefing() {
  const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
  const { data: briefingData, error, isLoading } = useSWR(`${apiBase}/api/briefing`, fetcher)
  const [isGenerating, setIsGenerating] = useState(false)

  const handleRefresh = async () => {
    setIsGenerating(true)
    try {
      const res = await fetch(`${apiBase}/api/briefing/audit`, { method: 'POST' })
      if (res.ok) {
        await mutate(`${apiBase}/api/briefing`)
      }
    } catch (err) {
      console.error("Audit failed", err)
    } finally {
      setTimeout(() => setIsGenerating(false), 1000)
    }
  }

  if (isLoading) return <div className="p-12 text-center animate-pulse text-gold-400">📊 AI is auditing your business data...</div>
  if (!briefingData || error) return <div className="p-12 text-center text-red-400">❌ Failed to load briefing. Is backend running?</div>

  return (
    <div className="space-y-6 animate-in fade-in duration-700">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-card p-6 rounded-2xl border border-gold-500/20 shadow-xl shadow-gold-500/5">
        <div className="flex items-center gap-4">
          <Link href="/" className="p-2 rounded-xl bg-muted hover:bg-muted/80 transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="w-5 h-5 text-gold-400 animate-pulse" />
              <h1 className="text-2xl font-bold text-gradient">Monday Morning CEO Briefing</h1>
            </div>
            <p className="text-muted-foreground text-sm">Automated Business Audit for {briefingData.period}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={handleRefresh} 
            disabled={isGenerating}
            className={`btn-secondary flex items-center gap-2 ${isGenerating ? 'opacity-50 cursor-wait' : ''}`}
          >
            <Zap className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
            {isGenerating ? 'Auditing...' : 'Re-Audit Now'}
          </button>
          <button className="btn-primary flex items-center gap-2">
            <Download className="w-4 h-4" /> Export PDF
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* LEFT COLUMN: Financials & Metrics */}
        <div className="lg:col-span-2 space-y-6">

          {/* Executive Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="card-gold p-4 bg-green-500/5 border-green-500/20">
              <div className="flex justify-between items-start mb-2">
                <DollarSign className="text-green-400 w-5 h-5" />
                <span className="text-xs font-bold text-green-400">{briefingData.revenue?.growth || '0%'}</span>
              </div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">Total Revenue</p>
              <p className="text-xl font-bold">{briefingData.revenue?.total || 'PKR 0'}</p>
            </div>

            <div className="card-gold p-4 bg-blue-500/5 border-blue-500/20">
              <div className="flex justify-between items-start mb-2">
                <Users className="text-blue-400 w-5 h-5" />
                <span className="badge-gold">{briefingData.leads?.new || 0} New</span>
              </div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">Business Leads</p>
              <p className="text-xl font-bold text-blue-400">{briefingData.leads?.total || 0} Total</p>
            </div>

            <div className="card-gold p-4 bg-purple-500/5 border-purple-500/20">
              <div className="flex justify-between items-start mb-2">
                <Target className="text-purple-400 w-5 h-5" />
                <span className="text-xs text-purple-400">100% Done</span>
              </div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">Target Status</p>
              <p className="text-xl font-bold">{briefingData.revenue?.status || 'N/A'}</p>
            </div>
          </div>
          {/* Social Media Insights Integration */}
          <div className="card-gold p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-gold-400" /> Multi-Platform Performance
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg border border-border">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-pink-500/20 flex items-center justify-center text-pink-400">IG</div>
                  <p className="text-sm">{briefingData.socialImpact?.instagram || 'Instagram campaign active'}</p>
                </div>
                <ArrowRight className="w-4 h-4 text-muted-foreground" />
              </div>
              <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg border border-border">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400">FB</div>
                  <p className="text-sm">{briefingData.socialImpact?.facebook || 'Facebook monitoring enabled'}</p>
                </div>
                <ArrowRight className="w-4 h-4 text-muted-foreground" />
              </div>
            </div>
          </div>

          {/* Bottlenecks / Error Handling */}
          <div className="card-gold p-6 border-red-500/20">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-red-400">
              <AlertCircle className="w-5 h-5" /> Efficiency Bottlenecks
            </h3>
            <div className="overflow-hidden rounded-lg border border-border">
              {(!briefingData.bottlenecks || briefingData.bottlenecks.length === 0) ? (
                <p className="p-4 text-sm text-muted-foreground italic text-center">No bottlenecks detected. System is running at 100% efficiency.</p>
              ) : (
                <table className="w-full text-sm text-left">
                  <thead className="bg-muted/50 text-muted-foreground uppercase text-[10px]">
                    <tr>
                      <th className="px-4 py-3">Blocked Task</th>
                      <th className="px-4 py-3">Delay</th>
                      <th className="px-4 py-3">AI Reason</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {briefingData.bottlenecks.map((item: any, i: number) => (
                      <tr key={i} className="hover:bg-muted/30">
                        <td className="px-4 py-3 font-medium">{item.task}</td>
                        <td className="px-4 py-3 text-red-400">{item.delay}</td>
                        <td className="px-4 py-3 text-muted-foreground">{item.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: AI Reasoning & Proactive Actions */}
        <div className="space-y-6">
          <div className="card-gold p-6 bg-gold-500/5 border-gold-500/30 h-full">
            <div className="flex items-center gap-2 mb-6">
              <Sparkles className="w-6 h-6 text-gold-400" />
              <h3 className="text-lg font-bold">Proactive Agent Suggestions</h3>
            </div>

            <div className="space-y-6">
              {!briefingData.aiSuggestions || briefingData.aiSuggestions.length === 0 ? (
                <p className="text-sm text-muted-foreground italic">No new suggestions at this time.</p>
              ) : (
                briefingData.aiSuggestions.map((suggest: any) => (
                  <div key={suggest.id} className="relative pl-6 border-l-2 border-gold-500/30 space-y-2 group">
                    <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-background border-2 border-gold-500" />
                    <p className="text-sm leading-relaxed group-hover:text-gold-400 transition-colors">
                      {suggest.text}
                    </p>
                    <div className="flex gap-2">
                      <button className="text-[10px] font-bold uppercase tracking-widest text-green-400 hover:underline">Approve</button>
                      <button className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground hover:underline">Reject</button>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="mt-12 p-4 rounded-xl bg-muted/50 border border-dashed border-border text-center">
              <p className="text-xs text-muted-foreground mb-3 italic">
                &quot;AI Employee is waiting for your approval to execute the cost-saving tasks.&quot;
              </p>
              <button className="btn-primary w-full text-xs">Execute Approved Actions</button>
            </div>
          </div>
        </div>

      </div>

      {/* Audit Log (Footer) */}
      <div className="flex items-center justify-between text-[10px] text-muted-foreground uppercase tracking-widest px-2">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="w-3 h-3 text-green-500" />
          Audit Verified by Gemini Code Engine
        </div>
        <div>System Version: Gold-Tier v1.4.2</div>
      </div>
    </div>
  )
}

