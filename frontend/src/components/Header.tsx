'use client'

import React, { useState, useEffect } from 'react'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import {
  Bell,
  Search,
  Menu,
  User,
  Settings,
  LogOut,
  ChevronDown,
  Circle,
  Users,
  X,
  Clock,
  Shield,
  CheckCircle,
  Server,
  BarChart,
  FileText,
  DollarSign,
  Activity as ActivityIcon
} from 'lucide-react'
import NotificationsPanel from './NotificationsPanel'
import SettingsModal from './SettingsModal'
import { Notification, ModalType } from '@/types'

const USER_IMAGE_URL = 'https://api.dicebear.com/7.x/avataaars/svg?seed=Jenny'
const LOGO_URL = '/k-ele - Copy.jpg'

interface HeaderProps {
  sidebarOpen: boolean
  onToggleSidebar: () => void
  onOpenModal?: (type: ModalType) => void
}

interface SearchItem {
  id: string
  type: 'task' | 'approval' | 'notification' | 'done' | 'page' | 'lead'
  title: string
  category?: string
  status?: string
  priority?: string
  amount?: string
  completedAt?: string
  href?: string
}

export default function Header({ onToggleSidebar, onOpenModal }: HeaderProps) {
  const router = useRouter()
  const [searchFocused, setSearchFocused] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [notifOpen, setNotifOpen] = useState(false)
  const [showFullPanel, setShowFullPanel] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [headerNotifs, setHeaderNotifs] = useState<Notification[]>([])
  const [liveLeads, setLiveLeads] = useState<any[]>([])
  const [systemStatus, setSystemStatus] = useState({ watchers: 0, mcp_servers: 7 })

  // Fetch live data
  useEffect(() => {
    const fetchData = async () => {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
      
      try {
        const [leadsRes, activityRes, dashboardRes] = await Promise.all([
          fetch(`${apiBase}/api/leads`),
          fetch(`${apiBase}/api/activity?hours=1`),
          fetch(`${apiBase}/api/dashboard`)
        ])

        if (leadsRes.ok) {
          const leadsData = await leadsRes.json()
          setLiveLeads(leadsData.leads || [])
          
          if (activityRes.ok) {
            const activityData = await activityRes.json()
            const newNotifs: Notification[] = [
              ...leadsData.leads.slice(-5).map((l: any) => ({
                id: l.id || `lead_${l.created || Date.now()}`,
                title: `New Lead: ${l.name}`,
                desc: l.comment ? l.comment.substring(0, 60) + '...' : 'No comment provided',
                time: l.created ? new Date(l.created).toLocaleTimeString() : 'Just now',
                read: false,
                type: 'lead'
              })),
              ...activityData.activity.slice(0, 5).map((a: any, i: number) => ({
                id: a.id || `act_${a.timestamp}_${i}`,
                title: a.action.replace(/_/g, ' '),
                desc: a.description ? a.description.substring(0, 60) + '...' : 'No description provided',
                time: a.timestamp ? new Date(a.timestamp).toLocaleTimeString() : 'Just now',
                read: false,
                type: 'alert'
              }))
            ]
            setHeaderNotifs(newNotifs)
          }
        }

        if (dashboardRes.ok) {
          const dashData = await dashboardRes.json()
          if (dashData.system_status) {
            setSystemStatus({
              watchers: dashData.system_status.watchers || 0,
              mcp_servers: dashData.system_status.mcp_servers || 7
            })
          }
        }
      } catch (error) {
        console.error("Failed to fetch header data:", error)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])

  const unread = headerNotifs.filter(n => !n.read).length

  // Build searchable data including pages and live leads
  const getSearchableItems = (): SearchItem[] => {
    const pages: SearchItem[] = [
      { id: 'p1', type: 'page', title: 'Dashboard Home', category: 'Navigation', href: '/' },
      { id: 'p2', type: 'page', title: 'Revenue Insights', category: 'Analytics', href: '/revenue' },
      { id: 'p3', type: 'page', title: 'CEO Briefings & Audit', category: 'Reporting', href: '/briefings' },
      { id: 'p4', type: 'page', title: 'Accounting & Invoices', category: 'Finance', href: '/accounting' },
      { id: 'p5', type: 'page', title: 'System Settings', category: 'Config', href: '/settings' },
      { id: 'p6', type: 'page', title: 'Live Activity Log', category: 'System', href: '/activity' },
    ]

    const leads: SearchItem[] = liveLeads.map((l, i) => ({
      id: `lead_${i}`,
      type: 'lead',
      title: `Lead: ${l.name}`,
      category: l.source || 'Facebook',
      status: l.status || 'New',
    }))

    const mockTasks: SearchItem[] = [
      { id: 't1', type: 'task', title: 'Review pending invoice #1024', category: 'Finance', status: 'pending', priority: 'high' },
      { id: 't2', type: 'task', title: 'Reply to customer complaint', category: 'WhatsApp', status: 'pending', priority: 'medium' },
      { id: 'a1', type: 'approval', title: 'Invoice payment PKR 45,000', category: 'Finance', amount: '45000', status: 'waiting' },
    ]

    return [...pages, ...leads, ...mockTasks]
  }

  const searchResults = searchQuery.trim().length >= 2
    ? getSearchableItems().filter(item =>
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (item.category && item.category.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : []

  const handleSearchSelect = (item: SearchItem) => {
    setSearchQuery('')
    setSearchFocused(false)

    if (item.type === 'page' && item.href) {
      router.push(item.href)
    } else if (item.type === 'notification') {
      setShowFullPanel(true)
    } else if (item.type === 'approval' || item.type === 'lead') {
      onOpenModal?.('odoo')
    } else if (item.id === 'p5') {
      setShowSettings(true)
    }
  }

  const clearSearch = () => {
    setSearchQuery('')
    setSearchFocused(false)
  }

  const markRead = (id: string) => {
    setHeaderNotifs(prev => prev.map(n => n.id === id ? { ...n, read: true } : n))
  }

  const markAllRead = () => {
    setHeaderNotifs(prev => prev.map(n => ({ ...n, read: true })))
  }

  // Sync notifications from full panel back to header
  const handleSyncNotifs = React.useCallback((notifs: Notification[]) => {
    setHeaderNotifs(notifs.slice(0, 10))
  }, [])

  // If showing full notifications panel
  if (showFullPanel) {
    return (
      <div className="fixed inset-0 z-50 bg-background">
        <NotificationsPanel
          onBack={() => setShowFullPanel(false)}
          onSync={handleSyncNotifs}
          onOpenModal={onOpenModal}
        />
      </div>
    )
  }

  // If showing settings
  if (showSettings) {
    return (
      <div className="fixed inset-0 z-50 bg-background">
        <SettingsModal onClose={() => setShowSettings(false)} />
      </div>
    )
  }

  return (
    <header className="h-20 bg-card/50 backdrop-blur-xl border-b border-border px-6 flex items-center justify-between">
      {/* Left Section */}
      <div className="flex items-center gap-4">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-2 rounded-lg hover:bg-muted transition-colors"
        >
          <Menu className="w-6 h-6" />
        </button>

        {/* Main Logo */}
        <div className="flex items-center gap-3 pr-4 border-r border-border/50">
          <div className="w-10 h-10 rounded-xl overflow-hidden border border-gold-500/30 bg-white flex items-center justify-center p-1 shadow-inner">
            <Image
               src={LOGO_URL}
               alt="K-Electric Logo"
               width={40}
               height={40}
               className="w-full h-full object-contain"
             />
          </div>
          <span className="hidden xl:block text-lg font-bold text-gradient">K-Electric</span>
        </div>

        {/* Search Bar */}
        <div className={`relative transition-all duration-300 ${searchFocused ? 'w-[400px]' : 'w-56'}`}>
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search tasks, approvals, briefings..."
            value={searchQuery}
            onChange={(e) => { setSearchQuery(e.target.value); setSearchFocused(true) }}
            onFocus={() => setSearchFocused(true)}
            onBlur={() => {
              // Delay closing to allow click on results
              setTimeout(() => setSearchFocused(false), 200)
            }}
            className="input-gold pl-10 pr-10 py-2"
          />
          {searchQuery && (
            <button
              onClick={clearSearch}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="w-4 h-4" />
            </button>
          )}

          {/* Search Results Dropdown */}
          {searchFocused && searchQuery.trim().length >= 2 && (
            <div className="absolute top-full left-0 mt-2 w-full bg-card border border-border rounded-xl shadow-2xl shadow-black/50 z-50 overflow-hidden">
              {searchResults.length === 0 ? (
                <div className="px-5 py-8 text-center">
                  <Search className="w-8 h-8 mx-auto mb-2 text-muted-foreground/30" />
                  <p className="text-sm text-muted-foreground">No results for &quot;{searchQuery}&quot;</p>
                  <p className="text-xs text-muted-foreground/50 mt-1">Try searching for tasks, approvals, or notifications</p>
                </div>
              ) : (
                <>
                  <div className="px-4 py-2 bg-muted/50 border-b border-border">
                    <p className="text-xs text-muted-foreground">{searchResults.length} result{searchResults.length !== 1 ? 's' : ''} found</p>
                  </div>
                  <div className="max-h-80 overflow-y-auto">
                    {searchResults.map((result) => (
                      <button
                        key={result.id}
                        onClick={() => handleSearchSelect(result)}
                        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-muted/50 transition-colors border-b border-border/50 last:border-b-0 text-left"
                      >
                        {/* Type Icon */}
                        <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
                          result.type === 'task' ? 'bg-orange-500/20 text-orange-400' :
                          result.type === 'approval' ? 'bg-gold-500/20 text-gold-400' :
                          result.type === 'notification' ? 'bg-blue-500/20 text-blue-400' :
                          result.type === 'page' ? 'bg-purple-500/20 text-purple-400' :
                          result.type === 'lead' ? 'bg-blue-500/20 text-blue-400' :
                          'bg-green-500/20 text-green-400'
                        }`}>
                          {result.type === 'task' && <Clock className="w-4 h-4" />}
                          {result.type === 'approval' && <Shield className="w-4 h-4" />}
                          {result.type === 'notification' && <Bell className="w-4 h-4" />}
                          {result.type === 'done' && <CheckCircle className="w-4 h-4" />}
                          {result.type === 'page' && <ActivityIcon className="w-4 h-4" />}
                          {result.type === 'lead' && <Users className="w-4 h-4" />}
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{result.title}</p>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-muted-foreground">{result.category}</span>
                            {result.priority && (
                              <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                                result.priority === 'high' ? 'bg-red-500/20 text-red-400' :
                                result.priority === 'medium' ? 'bg-gold-500/20 text-gold-400' :                                'bg-green-500/20 text-green-400'
                              }`}>
                                {result.priority}
                              </span>
                            )}
                            {result.amount && (
                              <span className="text-xs text-green-400">PKR {result.amount}</span>
                            )}
                          </div>
                        </div>

                        {/* Type Badge */}
                        <span className="text-[10px] px-2 py-1 rounded-full bg-muted border border-border text-muted-foreground shrink-0 capitalize">
                          {result.type}
                        </span>
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-4">
        {/* Live Status */}
        <div className="hidden lg:flex items-center gap-4 px-4 py-2 rounded-full bg-muted/50 border border-border">
          <div className="flex items-center gap-2 pr-4 border-r border-border/50">
            <Circle className="w-2 h-2 text-green-500 animate-pulse" />
            <span className="text-xs font-bold text-green-400">System Live</span>
          </div>
          <div className="flex items-center gap-4 text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
             <span className="flex items-center gap-1.5">
                <Users className="w-3 h-3 text-blue-400" />
                {systemStatus.watchers} Watchers
             </span>
             <span className="flex items-center gap-1.5">
                <Server className="w-3 h-3 text-gold-400" />
                {systemStatus.mcp_servers} MCP Servers
             </span>
          </div>
        </div>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setNotifOpen(!notifOpen)}
            className="relative p-2 rounded-lg hover:bg-muted transition-all duration-300 hover:scale-110"
          >
            <Bell className="w-6 h-6" />
            {unread > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-gold-500 text-background text-xs font-bold rounded-full flex items-center justify-center animate-pulse">
                {unread}
              </span>
            )}
          </button>

          {/* Notification Dropdown Panel */}
          {notifOpen && (
            <>
              {/* Backdrop */}
              <div className="fixed inset-0 z-40" onClick={() => setNotifOpen(false)} />

              <div className="absolute right-0 top-full mt-3 w-96 bg-card border border-border rounded-2xl shadow-2xl shadow-black/50 z-50 overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between px-5 py-4 border-b border-border bg-gradient-to-r from-gold-500/10 to-transparent">
                  <h3 className="text-lg font-bold">Notifications</h3>
                  <button
                    onClick={markAllRead}
                    className="text-xs text-gold-500 hover:text-gold-400 font-medium"
                  >
                    Mark all read
                  </button>
                </div>

                {/* List */}
                <div className="max-h-80 overflow-y-auto">
                  {headerNotifs.length === 0 ? (
                    <div className="px-5 py-10 text-center text-muted-foreground">
                      <Bell className="w-10 h-10 mx-auto mb-3 opacity-30" />
                      <p>No notifications yet</p>
                    </div>
                  ) : (
                    headerNotifs.map((notif) => (
                      <div
                        key={notif.id}
                        onClick={() => markRead(notif.id)}
                        className={`
                          px-5 py-4 border-b border-border/50 cursor-pointer
                          transition-colors hover:bg-muted/50
                          ${!notif.read ? 'bg-gold-500/5 border-l-2 border-l-gold-500' : ''}
                        `}
                      >
                        <div className="flex items-start gap-3">
                          {/* Icon */}
                          <div className={`
                            w-9 h-9 rounded-full flex items-center justify-center shrink-0
                            ${notif.type === 'lead' ? 'bg-blue-500/20 text-blue-400' : ''}
                            ${notif.type === 'payment' ? 'bg-green-500/20 text-green-400' : ''}
                            ${notif.type === 'task' ? 'bg-purple-500/20 text-purple-400' : ''}
                          `}>
                            {notif.type === 'lead' && <User className="w-4 h-4" />}
                            {notif.type === 'payment' && <Circle className="w-4 h-4" />}
                            {notif.type === 'task' && <Settings className="w-4 h-4" />}
                          </div>

                          {/* Content */}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold truncate">{notif.title}</p>
                            <p className="text-xs text-muted-foreground mt-0.5 truncate">{notif.desc}</p>
                            <p className="text-[10px] text-muted-foreground/60 mt-1">{notif.time}</p>
                          </div>

                          {/* Unread dot */}
                          {!notif.read && (
                            <div className="w-2 h-2 rounded-full bg-gold-500 mt-2 shrink-0" />
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Footer */}
                <div className="px-5 py-3 border-t border-border bg-muted/30">
                  <button
                    onClick={() => { setNotifOpen(false); setShowFullPanel(true) }}
                    className="text-xs text-gold-500 hover:text-gold-400 font-medium w-full text-center"
                  >
                    View all notifications →
                  </button>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Settings */}
        <button
          onClick={() => setShowSettings(true)}
          className="p-2 rounded-lg hover:bg-muted transition-all duration-300 hover:scale-110 hover:rotate-90"
          title="Settings"
        >
          <Settings className="w-6 h-6" />
        </button>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setUserMenuOpen(!userMenuOpen)}
            className="flex items-center gap-3 pl-4 border-l border-border hover:bg-muted/30 rounded-xl px-4 py-2 transition-colors"
          >
            <div className="w-10 h-10 rounded-full overflow-hidden shadow-lg shadow-gold-500/30">
              <Image
                src={USER_IMAGE_URL}
                alt="User"
                width={40}
                height={40}
                className="w-full h-full object-cover"
                style={{ width: 'auto', height: 'auto' }}
              />
            </div>
            <div className="text-left">
              <p className="text-sm font-semibold">Admin User</p>
              <p className="text-xs text-muted-foreground">Gold Tier Access</p>
            </div>
            <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* User Dropdown */}
          {userMenuOpen && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} />
              <div className="absolute right-0 top-full mt-2 w-72 bg-card border border-border rounded-2xl shadow-2xl shadow-black/50 z-50 overflow-hidden">
                {/* User Info */}
                <div className="px-5 py-4 border-b border-border bg-gradient-to-r from-gold-500/10 to-transparent">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full overflow-hidden shadow-md">
                      <Image
                        src={USER_IMAGE_URL}
                        alt="User"
                        width={48}
                        height={48}
                        className="w-full h-full object-cover"
                        style={{ width: 'auto', height: 'auto' }}
                      />
                    </div>
                    <div>
                      <p className="font-bold">Admin User</p>
                      <p className="text-xs text-gold-500 font-medium">Gold Tier Access</p>
                      <p className="text-[10px] text-muted-foreground">digitaldreamers18@gmail.com</p>
                    </div>
                  </div>
                </div>

                {/* Menu Items */}
                <div className="py-2">
                  <button
                    onClick={() => { setUserMenuOpen(false); setShowSettings(true) }}
                    className="w-full flex items-center gap-3 px-5 py-3 text-sm hover:bg-muted/50 transition-colors"
                  >
                    <Settings className="w-4 h-4 text-muted-foreground" />
                    <span>Settings</span>
                  </button>
                  <button
                    onClick={() => { setUserMenuOpen(false); setShowFullPanel(true) }}
                    className="w-full flex items-center gap-3 px-5 py-3 text-sm hover:bg-muted/50 transition-colors"
                  >
                    <Bell className="w-4 h-4 text-muted-foreground" />
                    <span>Notifications</span>
                    {unread > 0 && (
                      <span className="ml-auto w-5 h-5 bg-gold-500 text-background text-xs font-bold rounded-full flex items-center justify-center">
                        {unread}
                      </span>
                    )}
                  </button>
                  <button
                    onClick={() => { setUserMenuOpen(false); onOpenModal?.('odoo') }}
                    className="w-full flex items-center gap-3 px-5 py-3 text-sm hover:bg-muted/50 transition-colors"
                  >
                    <Server className="w-4 h-4 text-muted-foreground" />
                    <span>Odoo CRM</span>
                  </button>
                  <button
                    onClick={() => { setUserMenuOpen(false); onOpenModal?.('facebook') }}
                    className="w-full flex items-center gap-3 px-5 py-3 text-sm hover:bg-muted/50 transition-colors"
                  >
                    <Users className="w-4 h-4 text-muted-foreground" />
                    <span>Facebook Dashboard</span>
                  </button>
                </div>

                {/* Logout */}
                <div className="border-t border-border py-2">
                  <button
                    onClick={() => { setUserMenuOpen(false); alert('Logout functionality coming soon!') }}
                    className="w-full flex items-center gap-3 px-5 py-3 text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Logout</span>
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
