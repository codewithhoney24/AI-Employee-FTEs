'use client'

import CEOBriefing from '@/components/CEOBriefing'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import { useState } from 'react'

export default function BriefingPage() {
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
          <div className="max-w-7xl mx-auto pb-12">
            <CEOBriefing />
          </div>
        </main>
      </div>
    </div>
  )
}
