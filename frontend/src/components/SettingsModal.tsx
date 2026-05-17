'use client'

import React, { useState } from 'react'
import {
  X, Settings, Bell, Shield, User, Globe, Database, Moon
} from 'lucide-react'

interface SettingsModalProps {
  onClose: () => void
}

export default function SettingsModal({ onClose }: SettingsModalProps) {
  return (
    <div className="fixed inset-0 z-[110] flex items-center justify-center p-4">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-4xl bg-card border border-border rounded-2xl shadow-2xl overflow-hidden flex h-[70vh]">

        {/* Sidebar */}
        <div className="w-64 border-r border-border bg-muted/30 p-4">
          <div className="flex items-center gap-3 mb-8 px-2">
            <Settings className="w-6 h-6 text-gold-400" />
            <h2 className="text-xl font-bold">Settings</h2>
          </div>

          <nav className="space-y-1">
            <SettingsNavItem icon={User} label="Profile" active />
            <SettingsNavItem icon={Bell} label="Notifications" />
            <SettingsNavItem icon={Shield} label="Security" />
            <SettingsNavItem icon={Globe} label="Integrations" />
            <SettingsNavItem icon={Database} label="Data Management" />
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 flex flex-col bg-card">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-border">
            <h3 className="text-lg font-bold">User Profile</h3>
            <button
              onClick={onClose}
              className="p-2 hover:bg-muted rounded-full transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Body */}
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

                {/* Static toggle (UI only) */}
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

          {/* Footer */}
          <div className="p-6 border-t border-border flex justify-end gap-4 bg-muted/10">
            <button
              onClick={onClose}
              className="btn-secondary py-2 px-6 text-sm"
            >
              Cancel
            </button>
            <button className="btn-primary py-2 px-6 text-sm">
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ================= COMPONENTS ================= */

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