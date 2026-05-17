'use client'

import React, { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import Link from 'next/link'
import { 
  Bell, Shield, User, Globe, Database, Moon, ArrowLeft 
} from 'lucide-react'

export default function SettingsPage() {
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
        
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-muted/20">
          <div className="max-w-5xl mx-auto h-full flex flex-col">
            <div className="mb-6 flex items-center gap-4">
              <Link 
                href="/" 
                className="p-2 rounded-xl bg-card border border-border hover:bg-muted transition-all hover:scale-110 shadow-sm"
                title="Back to Dashboard"
              >
                <ArrowLeft className="w-5 h-5 text-gold-400" />
              </Link>
              <div>
                <h1 className="text-3xl font-bold text-gradient">System Settings</h1>
                <p className="text-muted-foreground mt-1">Manage your KE AI Employee configuration and integrations.</p>
              </div>
            </div>
            
            <div className="flex-1 bg-card rounded-2xl border border-border shadow-xl overflow-hidden min-h-[600px]">
               {/* Embed the SettingsModal logic directly without the fixed positioning overlay */}
               <div className="flex h-full">
                  {/* Reuse Sidebar Logic from SettingsModal if possible or implement inline */}
                  <SettingsLayout />
               </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

function SettingsLayout() {
  // Extracting logic from SettingsModal for full-page use
  return (
     <div className="flex w-full h-full">
        {/* Settings Sidebar */}
        <div className="w-64 border-r border-border bg-muted/30 p-4 hidden md:block">
          <nav className="space-y-1">
            <SettingsNavItem icon={User} label="Profile" active />
            <SettingsNavItem icon={Bell} label="Notifications" />
            <SettingsNavItem icon={Shield} label="Security" />
            <SettingsNavItem icon={Globe} label="Integrations" />
            <SettingsNavItem icon={Database} label="Data Management" />
          </nav>
        </div>

        {/* Settings Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
           <div className="flex-1 overflow-y-auto p-8 space-y-8">
              {/* Appearance */}
              <section className="space-y-4">
                <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                  Appearance
                </h4>

                <div className="flex items-center justify-between p-4 rounded-xl bg-muted/30 border border-border">
                  <div className="flex items-center gap-3">
                    <Moon className="w-5 h-5 text-gold-400" />
                    <div>
                      <p className="font-medium">Dark Mode</p>
                      <p className="text-xs text-muted-foreground">
                        Always stay in the shadows
                      </p>
                    </div>
                  </div>

                  <div className="w-12 h-6 bg-gold-500 rounded-full relative cursor-pointer">
                    <div className="absolute right-1 top-1 w-4 h-4 bg-background rounded-full" />
                  </div>
                </div>
              </section>

              {/* Notifications */}
              <section className="space-y-4">
                <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                  System Notifications
                </h4>

                <div className="space-y-3">
                  <ToggleSetting
                    label="Email Alerts"
                    description="Receive daily summaries"
                    defaultChecked
                  />
                  <ToggleSetting
                    label="Lead Notifications"
                    description="Real-time Facebook lead alerts"
                    defaultChecked
                  />
                  <ToggleSetting
                    label="Security Alerts"
                    description="Notify on unauthorized access attempts"
                    defaultChecked
                  />
                </div>
              </section>

              {/* Gold Tier */}
              <section className="space-y-4">
                <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                  Gold Tier Features
                </h4>

                <div className="p-4 rounded-xl bg-gold-500/5 border border-gold-500/20">
                  <p className="text-sm font-medium text-gold-400">
                    Ralph Wiggum AI Loop
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Autonomous decision making is currently active and processing background tasks.
                  </p>
                </div>
              </section>
           </div>
           
           <div className="p-6 border-t border-border flex justify-end gap-4 bg-muted/10">
              <button className="btn-secondary py-2 px-6 text-sm">Cancel</button>
              <button className="btn-primary py-2 px-6 text-sm">Save Changes</button>
           </div>
        </div>
     </div>
  )
}

function SettingsNavItem({
  icon: Icon,
  label,
  active = false,
}: {
  icon: React.ElementType
  label: string
  active?: boolean
}) {
  return (
    <button
      className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm ${
        active
          ? 'bg-gold-500/10 text-gold-400 font-semibold'
          : 'text-muted-foreground hover:bg-muted hover:text-foreground'
      }`}
    >
      <Icon className="w-4 h-4" />
      <span>{label}</span>
    </button>
  )
}

function ToggleSetting({
  label,
  description,
  defaultChecked = false,
}: {
  label: string
  description: string
  defaultChecked?: boolean
}) {
  const [enabled, setEnabled] = useState(defaultChecked)

  return (
    <div className="flex items-center justify-between p-4 rounded-xl bg-muted/20 border border-border/50">
      <div>
        <p className="text-sm font-medium">{label}</p>
        <p className="text-[11px] text-muted-foreground">{description}</p>
      </div>

      <div
        onClick={() => setEnabled(!enabled)}
        className={`w-10 h-5 rounded-full relative cursor-pointer transition-colors ${
          enabled ? 'bg-gold-500' : 'bg-muted-foreground/30'
        }`}
      >
        <div
          className={`absolute top-1 w-3 h-3 bg-background rounded-full transition-all ${
            enabled ? 'right-1' : 'left-1'
          }`}
        />
      </div>
    </div>
  )
}
