'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Mail, Phone, Cloud, Camera, Zap, Server, Shield, Briefcase,
  Home, DollarSign, Settings, FileText, BarChart, Sparkles, Menu
} from 'lucide-react'

interface Integration {
  icon: React.ElementType
  label: string
  status: 'active' | 'inactive' | 'error'
  type: string
}

const initialIntegrations: Integration[] = [
  { icon: Mail, label: 'Gmail', status: 'inactive', type: 'gmail' },
  { icon: Phone, label: 'WhatsApp', status: 'inactive', type: 'whatsapp' },
  { icon: Cloud, label: 'Facebook', status: 'inactive', type: 'facebook' },
  { icon: Camera, label: 'Instagram', status: 'inactive', type: 'instagram' },
  { icon: Briefcase, label: 'LinkedIn', status: 'inactive', type: 'linkedin' },
  { icon: Zap, label: 'Twitter (X)', status: 'inactive', type: 'twitter' },
  { icon: Server, label: 'Odoo ERP', status: 'inactive', type: 'odoo' },
  { icon: Shield, label: 'Security', status: 'active', type: 'security' },
]

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
  onOpenModal: (type: string) => void
}

export default function Sidebar({ isOpen, onToggle, onOpenModal }: SidebarProps) {
  const pathname = usePathname()
  const [integrations, setIntegrations] = useState<Integration[]>(initialIntegrations)

  useEffect(() => {
    const fetchStatuses = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
        const res = await fetch(`${apiBase}/api/platforms/status`)
        if (res.ok) {
          const statuses = await res.json()
          setIntegrations(prev => prev.map(integration => ({
            ...integration,
            status: statuses[integration.type] || integration.status
          })))
        }
      } catch (error) {
        console.error("Failed to fetch platform statuses:", error)
      }
    }

    fetchStatuses()
    const interval = setInterval(fetchStatuses, 10000) // Update every 10s
    return () => clearInterval(interval)
  }, [])

  return (
    <aside
      className={`
        ${isOpen ? 'w-64' : 'w-20'}
        bg-card border-r border-border p-4 flex flex-col h-full shadow-lg transition-all duration-300 relative z-50
      `}
    >
      {/* Logo Area */}
      <div className={`flex items-center justify-between mb-8 px-2 ${!isOpen && 'flex-col gap-4'}`}>
        <div className="flex items-center gap-3">
          <Sparkles className="w-8 h-8 text-gold-400 animate-pulse shrink-0" />
          {isOpen && (
            <h1 className="text-xl font-bold text-foreground truncate">
              KE AI Employee
            </h1>
          )}
        </div>
        
        <button
          onClick={onToggle}
          className={`p-1.5 rounded-lg hover:bg-muted transition-colors text-muted-foreground ${!isOpen && 'w-full flex justify-center'}`}
          title={isOpen ? "Collapse Sidebar" : "Expand Sidebar"}
        >
          <Menu className={`w-5 h-5 transition-transform ${isOpen ? '' : 'rotate-180'}`} />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2 overflow-y-auto no-scrollbar">
        <SidebarLink icon={Home} label="Dashboard" href="/" pathname={pathname} isOpen={isOpen} />
        <SidebarLink icon={BarChart} label="Revenue Insights" href="/revenue" pathname={pathname} isOpen={isOpen} />
        <SidebarLink icon={FileText} label="CEO Briefings" href="/briefings" pathname={pathname} isOpen={isOpen} />
        <SidebarLink icon={DollarSign} label="Accounting" href="/accounting" pathname={pathname} isOpen={isOpen} />
        <SidebarLink icon={Settings} label="Settings" href="/settings" pathname={pathname} isOpen={isOpen} />

        {/* Integrations */}
        <div className={`pt-4 border-t border-border mt-4 ${!isOpen && 'flex flex-col items-center'}`}>
          {isOpen && (
            <h2 className="text-xs uppercase text-muted-foreground font-semibold px-2 mb-2">
              Integrations
            </h2>
          )}

          {integrations.map((integration) => (
            <button
              key={integration.type}
              onClick={() => onOpenModal(integration.type)}
              className={`
                w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors
                text-muted-foreground hover:bg-muted hover:text-foreground mb-1 group relative
                ${!isOpen && 'justify-center'}
              `}
            >
              <integration.icon className="w-5 h-5 shrink-0 group-hover:text-gold-400 transition-colors" />

              {isOpen && (
                <>
                  <span className="flex-1 text-left">{integration.label}</span>
                  <span
                    className={`w-2 h-2 rounded-full ${
                      integration.status === 'active'
                        ? 'bg-green-500'
                        : integration.status === 'error'
                        ? 'bg-red-500'
                        : 'bg-gold-500'                    }`}
                  />
                </>
              )}

              {!isOpen && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-popover text-popover-foreground text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50 shadow-xl border border-border">
                  {integration.label}
                </div>
              )}
            </button>
          ))}
        </div>
      </nav>

      {/* Footer */}
      <div className="mt-auto pt-4 border-t border-border text-center">
        <p className="text-[10px] text-muted-foreground uppercase tracking-widest">
          {isOpen ? 'Gold Tier v1.0' : 'v1.0'}
        </p>
      </div>
    </aside>
  )
}

function SidebarLink({
  icon: Icon,
  label,
  href,
  pathname,
  isOpen,
}: {
  icon: React.ElementType
  label: string
  href: string
  pathname: string
  isOpen: boolean
}) {
  const isActive = pathname === href

  return (
    <Link
      href={href}
      className={`
        flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group relative
        ${
          isActive
            ? 'bg-gold-500 text-background font-bold shadow-lg shadow-gold-500/20'
            : 'text-muted-foreground hover:bg-muted hover:text-foreground'
        }
        ${!isOpen && 'justify-center'}
      `}
    >
      <Icon className="w-5 h-5 shrink-0" />

      {isOpen && <span className="flex-1">{label}</span>}

      {!isOpen && (
        <div className="absolute left-full ml-2 px-2 py-1 bg-popover text-popover-foreground text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50 shadow-xl border border-border">
          {label}
        </div>
      )}
    </Link>
  )
}