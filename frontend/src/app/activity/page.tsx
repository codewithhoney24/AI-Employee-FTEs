'use client'

import React, { useState } from 'react'
import useSWR from 'swr'
import { Activity, ArrowLeft, Clock, Zap, MessageSquare, DollarSign, Users, Server } from 'lucide-react'
import Link from 'next/link'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

interface ActivityItem {
  id: string
  action: string
  details: {
    message: string
  }
  category: string
  timestamp: string
}

export default function ActivityPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [currentTime, setCurrentTime] = useState<string | null>(null)

  React.useEffect(() => {
    setCurrentTime(new Date().toLocaleTimeString())
  }, [])

  const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
  const { data, error } = useSWR(`${apiBase}/api/activity`, fetcher, {
    refreshInterval: 10000
  })

  const activities: ActivityItem[] = data?.activity || []

  const getIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'sales': return <Users className="w-4 h-4 text-blue-400" />
      case 'finance': return <DollarSign className="w-4 h-4 text-green-400" />
      case 'social': return <MessageSquare className="w-4 h-4 text-pink-400" />
      case 'system': return <Server className="w-4 h-4 text-purple-400" />
      default: return <Zap className="w-4 h-4 text-gold-400" />
    }
  }

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
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Link href="/" className="p-2 rounded-full hover:bg-muted transition-colors">
                  <ArrowLeft className="w-6 h-6" />
                </Link>
                <h1 className="text-3xl font-bold text-gradient">System Activity Logs</h1>
              </div>
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-gold-500/10 border border-gold-500/20">
                <div className="w-2 h-2 bg-gold-500 rounded-full animate-pulse" />
                <span className="text-xs text-gold-400 font-medium">Live Feed</span>
              </div>
            </div>

            <div className="card-gold divide-y divide-border/50">
              {activities.length === 0 ? (
                <div className="p-12 text-center text-muted-foreground italic">
                  No recent activity found.
                </div>
              ) : (
                activities.map((item) => (
                  <div key={item.id} className="p-4 hover:bg-muted/30 transition-colors flex items-start gap-4">
                    <div className="mt-1 p-2 rounded-lg bg-muted border border-border">
                      {getIcon(item.category)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                          {item.category}
                        </span>
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(item.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm font-medium mt-1">{item.details.message}</p>
                      <p className="text-xs text-muted-foreground mt-0.5">Action: {item.action.replace('_', ' ')}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
