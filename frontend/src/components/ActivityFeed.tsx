'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { Activity as ActivityIcon, CheckCircle, AlertCircle, Clock, Zap, Mail, MessageSquare, RefreshCw } from 'lucide-react'
import Link from 'next/link'

const iconMap: Record<string, React.ElementType> = {
  task_completed: CheckCircle,
  approval_updated: Zap,
  email_received: Mail,
  whatsapp_message: MessageSquare,
  error: AlertCircle,
  default: Clock,
}

interface ActivityItem {
  timestamp: string
  action: string
  category: string
  details: string
  status: string
}

interface RawActivityItem {
  timestamp: string
  action: string
  category?: string
  details?: string
  status?: string
}

export default function ActivityFeed() {
  const [activities, setActivities] = useState<ActivityItem[]>([])
  const [loading, setLoading] = useState(true)

  const fetchActivities = useCallback(async () => {
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
      const res = await fetch(`${apiBase}/api/activity?hours=1`)
      if (res.ok) {
        const data = await res.json()
        const normalized = (data.activity || []).map((item: any) => ({
          timestamp: item.timestamp,
          action: item.action || 'info',
          category: item.category || 'System',
          details: item.details?.message || item.details || item.action,
          status: item.status || 'success',
        }))

        setActivities(normalized)
      }
    } catch (err) {
      console.error("Failed to fetch activities", err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    const init = async () => {
      await fetchActivities()
    }
    init()
    
    const interval = setInterval(fetchActivities, 10000)
    return () => clearInterval(interval)
  }, [fetchActivities])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-400 bg-green-500/20 border-green-500/30'
      case 'error': return 'text-red-400 bg-red-500/20 border-red-500/30'
      case 'warning': return 'text-gold-400 bg-gold-500/20 border-gold-500/30'
      default: return 'text-muted-foreground bg-muted border-border'
    }
  }

  return (
    <div className="card-gold">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold">Activity Feed</h3>
          <p className="text-sm text-muted-foreground">Real-time system activity</p>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={() => { setLoading(true); fetchActivities(); }} 
            className={`p-2 rounded-lg hover:bg-muted transition-colors ${loading ? 'animate-spin' : ''}`}
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/20 border border-green-500/30">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-xs text-green-400 font-medium">Live</span>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {loading && activities.length === 0 ? (
          <div className="text-center py-4 text-muted-foreground">Loading activity feed...</div>
        ) : activities.length === 0 ? (
          <div className="text-center py-4 text-muted-foreground">No recent activity found.</div>
        ) : (
          activities.slice(0, 8).map((activity, index) => {
            const Icon = iconMap[activity.action] || iconMap.default

            return (
              <div
                key={`${activity.timestamp}-${index}`}
                className="flex items-start gap-4 p-3 rounded-lg hover:bg-muted/50 transition-all duration-300 group"
              >
                <div className={`
                  w-10 h-10 rounded-full flex items-center justify-center border
                  ${getStatusColor(activity.status)}
                  group-hover:scale-110 transition-transform duration-300
                `}>
                  <Icon className="w-5 h-5" />
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {typeof activity.details === 'object' ? JSON.stringify(activity.details) : activity.details}
                  </p>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-xs text-muted-foreground capitalize">
                      {activity.category}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(activity.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>

                <div className={`
                  w-2 h-2 rounded-full
                  ${activity.status === 'success' ? 'bg-green-500' : ''}
                  ${activity.status === 'error' ? 'bg-red-500' : ''}
                  ${activity.status === 'warning' ? 'bg-gold-500' : ''}
                `} />
              </div>
            )
          })
        )}
      </div>

      <div className="mt-4 pt-4 border-t border-border">
        <Link
          href="/activity"
          className="w-full flex items-center justify-center gap-2 text-center text-sm text-gold-400 hover:text-gold-300 hover:bg-gold-500/10 py-2 rounded-lg transition-all font-medium"
        >
          <ActivityIcon className="w-4 h-4" />
          View Full Activity Log
        </Link>
      </div>
    </div>
  )
}
