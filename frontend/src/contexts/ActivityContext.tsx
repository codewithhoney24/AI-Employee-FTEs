'use client'

import React, { createContext, useContext, useState, ReactNode } from 'react'

interface ActivityContextType {
  lastActivity: string | null
  setLastActivity: (activity: string) => void
}

const ActivityContext = createContext<ActivityContextType | undefined>(undefined)

export function ActivityProvider({ children }: { children: ReactNode }) {
  const [lastActivity, setLastActivity] = useState<string | null>(null)

  return (
    <ActivityContext.Provider value={{ lastActivity, setLastActivity }}>
      {children}
    </ActivityContext.Provider>
  )
}

export function useActivity() {
  const context = useContext(ActivityContext)
  if (context === undefined) {
    throw new Error('useActivity must be used within an ActivityProvider')
  }
  return context
}
