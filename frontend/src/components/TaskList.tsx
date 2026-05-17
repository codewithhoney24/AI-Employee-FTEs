'use client'
import React from 'react'
import useSWR from 'swr'
import { ClipboardList, AlertCircle, Clock } from 'lucide-react'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

interface Task {
  id: string
  title: string
  status: string
  priority: string
  type: string
}

export default function TaskList() {
  const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
  const { data, error } = useSWR(`${apiBase}/api/tasks`, fetcher, {
    refreshInterval: 5000
  })

  const tasks: Task[] = data?.tasks || []

  return (
    <div className="card-gold h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <ClipboardList className="w-5 h-5 text-gold-400" />
          Recent Tasks
        </h3>
        <span className="text-xs text-muted-foreground">{tasks.length} Active</span>
      </div>

      <div className="space-y-3">
        {tasks.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <Clock className="w-10 h-10 text-muted/30 mb-2" />
            <p className="text-sm text-muted-foreground italic">No active tasks found in Needs_Action.</p>
          </div>
        ) : (
          tasks.slice(0, 5).map((task) => (
            <div key={task.id} className="p-3 rounded-lg bg-muted/30 border border-border/50 hover:border-gold-500/30 transition-all group">
              <div className="flex items-start justify-between">
                <div className="flex gap-3">
                  <div className={`mt-1 w-2 h-2 rounded-full ${
                    task.priority === 'High' ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' : 'bg-gold-500'
                  }`} />
                  <div>
                    <p className="text-sm font-medium group-hover:text-gold-400 transition-colors">{task.title}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] uppercase tracking-wider text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                        {task.type}
                      </span>
                      <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" />
                        {task.priority} Priority
                      </span>
                    </div>
                  </div>
                </div>
                <button className="text-[10px] text-gold-400 opacity-0 group-hover:opacity-100 transition-opacity">
                  Process
                </button>
              </div>
            </div>
          ))
        )}
      </div>
      
      {tasks.length > 5 && (
        <button className="w-full mt-4 py-2 text-xs text-muted-foreground hover:text-gold-400 transition-colors border-t border-border/50">
          View all tasks ({tasks.length})
        </button>
      )}
    </div>
  )
}
