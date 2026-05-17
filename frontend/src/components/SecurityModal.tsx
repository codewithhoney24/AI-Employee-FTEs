'use client'

import React, { useState, useEffect } from 'react'
import {
  X, Shield, Eye, EyeOff,
  Key, Copy,
  Activity, Users, FileText, Bell,
  Zap, AlertTriangle, CheckCircle, Lock,
  Globe, Smartphone, Monitor, Cpu, Terminal,
  RefreshCcw, Search, Filter, ShieldCheck, ShieldAlert,
  Clock, User
} from 'lucide-react'

interface SecurityModalProps {
  onClose: () => void
}

/* ================= TYPES ================= */

type TabId = 'overview' | 'keys' | 'sessions' | 'audit' | 'alerts'

interface ApiKey {
  id: string
  name: string
  value: string
  expires: string
  daysLeft: number
  status: 'active' | 'inactive' | 'warning'
  lastUsed: string
}

interface AlertItem {
  id: string
  severity: 'critical' | 'warning' | 'info'
  message: string
  time: string
  resolved: boolean
  source: string
}

interface Session {
  id: string
  device: string
  location: string
  ip: string
  lastActive: string
  isCurrent: boolean
  type: 'mobile' | 'desktop' | 'bot'
}

interface AuditLogEntry {
  id: string
  action: string
  user: string
  timestamp: string
  status: 'success' | 'failure'
  ip: string
}

/* ================= COMPONENT ================= */

export default function SecurityModal({ onClose }: SecurityModalProps) {
  const [activeTab, setActiveTab] = useState<TabId>('overview')
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({})
  const [threatLevel, setThreatLevel] = useState(12)
  const [auditLog, setAuditLog] = useState<AuditLogEntry[]>([])
  const [sessions, setSessions] = useState<Session[]>([])
  const [isLive, setIsLive] = useState(true)

  // Live Data Simulation
  useEffect(() => {
    if (!isLive) return

    const interval = setInterval(() => {
      // Randomly change threat level
      setThreatLevel(prev => {
        const change = Math.floor(Math.random() * 5) - 2
        return Math.max(5, Math.min(45, prev + change))
      })

      // Add a random audit log entry occasionally
      if (Math.random() > 0.7) {
        const newEntry: AuditLogEntry = {
          id: Math.random().toString(36).substr(2, 9),
          action: ['Login Attempt', 'API Access', 'Settings Change', 'File Download', 'Admin Access'][Math.floor(Math.random() * 5)],
          user: ['Admin', 'Odoo Bot', 'System', 'Unknown User'][Math.floor(Math.random() * 4)],
          timestamp: new Date().toLocaleTimeString(),
          status: Math.random() > 0.9 ? 'failure' : 'success',
          ip: `182.163.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`
        }
        setAuditLog(prev => [newEntry, ...prev.slice(0, 19)])
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [isLive])

  // Initial Data
  useEffect(() => {
    const initialSessions: Session[] = [
      { id: '1', device: 'Windows Desktop - Chrome', location: 'Karachi, PK', ip: '182.163.102.45', lastActive: 'Active now', isCurrent: true, type: 'desktop' },
      { id: '2', device: 'iPhone 15 Pro - Safari', location: 'Lahore, PK', ip: '110.39.21.182', lastActive: '2 mins ago', isCurrent: false, type: 'mobile' },
      { id: '3', device: 'KE AI Engine - Worker Node', location: 'Frankfurt, DE', ip: '52.28.143.91', lastActive: 'Active now', isCurrent: false, type: 'bot' },
    ]
    setSessions(initialSessions)

    const initialAudit: AuditLogEntry[] = [
      { id: 'a1', action: 'Login Success', user: 'Admin', timestamp: '10:45 AM', status: 'success', ip: '182.163.102.45' },
      { id: 'a2', action: 'API Key Rotated', user: 'System', timestamp: '09:30 AM', status: 'success', ip: '127.0.0.1' },
      { id: 'a3', action: 'Failed Login', user: 'Unknown', timestamp: '04:12 AM', status: 'failure', ip: '45.227.253.109' },
    ]
    setAuditLog(initialAudit)
  }, [])

  const apiKeys: ApiKey[] = [
    { id: 'k1', name: 'Facebook Access Token', value: 'EAAj****70l7', expires: '2026-06-29', daysLeft: 58, status: 'warning', lastUsed: '5 mins ago' },
    { id: 'k2', name: 'Odoo API Secret', value: 'odoo****2026', expires: 'Never', daysLeft: -1, status: 'active', lastUsed: 'Active now' },
    { id: 'k3', name: 'Gemini API Key', value: 'AIza****9qXp', expires: '2027-01-15', daysLeft: 256, status: 'active', lastUsed: '2 mins ago' },
    { id: 'k4', name: 'SMTP Auth Token', value: 'smtp****pass', expires: '2026-12-01', daysLeft: 210, status: 'active', lastUsed: '1 hour ago' },
  ]

  const alerts: AlertItem[] = [
    { id: 'al1', severity: 'critical', message: 'Brute force attack detected from Russian IP 195.133.x.x', time: '12 mins ago', resolved: false, source: 'WAF' },
    { id: 'al2', severity: 'warning', message: 'Odoo session unauthorized attempt - check credentials', time: '1 hour ago', resolved: false, source: 'ERP Connector' },
    { id: 'al3', severity: 'info', message: 'Weekly security backup completed successfully', time: '3 hours ago', resolved: true, source: 'System' },
  ]

  const tabs: { id: TabId; label: string; icon: React.ElementType; color: string }[] = [
    { id: 'overview', label: 'Overview', icon: Activity, color: 'text-red-400' },
    { id: 'keys', label: 'API Keys', icon: Key, color: 'text-gold-400' },
    { id: 'sessions', label: 'Sessions', icon: Users, color: 'text-blue-400' },
    { id: 'audit', label: 'Audit Log', icon: FileText, color: 'text-green-400' },
    { id: 'alerts', label: 'Alerts', icon: Bell, color: 'text-red-500' },
  ]

  const toggleShow = (id: string) => {
    setShowKeys(prev => ({ ...prev, [id]: !prev[id] }))
  }

  const copyToClipboard = (val: string) => {
    navigator.clipboard.writeText(val)
    alert('Copied to clipboard!')
  }

  return (
    <div className="bg-card border border-border rounded-2xl shadow-2xl w-full max-w-6xl mx-auto flex flex-col h-[85vh] overflow-hidden">
      
      {/* HEADER */}
      <div className="flex items-center justify-between px-8 py-6 border-b border-border bg-gradient-to-r from-red-500/10 via-transparent to-transparent relative overflow-hidden shrink-0">
        <div className="absolute top-0 right-0 p-1 bg-red-500/10 border-b border-l border-red-500/20 rounded-bl-xl">
           <div className="flex items-center gap-2 px-3 py-1">
              <div className={`w-2 h-2 rounded-full ${isLive ? 'bg-red-500 animate-pulse' : 'bg-muted-foreground'}`} />
              <span className="text-[10px] font-bold uppercase tracking-widest text-red-400">
                {isLive ? 'Live Monitoring Active' : 'Monitoring Paused'}
              </span>
           </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-red-500/20 flex items-center justify-center border border-red-500/30 shadow-lg shadow-red-500/10">
            <Shield className="w-7 h-7 text-red-400" />
          </div>
          <div>
            <h2 className="text-2xl font-black tracking-tight flex items-center gap-2">
              SECURITY CENTER <span className="text-xs px-2 py-0.5 rounded bg-red-500 text-white font-bold">GOLD TIER</span>
            </h2>
            <p className="text-sm text-muted-foreground">
              Autonomous Threat Protection & Identity Management
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
           <button 
             onClick={() => setIsLive(!isLive)}
             className="p-3 rounded-xl hover:bg-muted border border-border transition-all"
             title={isLive ? "Pause Monitoring" : "Resume Monitoring"}
           >
             <RefreshCcw className={`w-5 h-5 ${isLive ? 'animate-spin-slow' : ''}`} />
           </button>
           <button onClick={onClose} className="p-3 rounded-xl hover:bg-muted border border-border transition-all group">
             <X className="w-6 h-6 group-hover:rotate-90 transition-transform" />
           </button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        
        {/* SIDEBAR NAVIGATION */}
        <div className="w-56 border-r border-border bg-muted/20 flex flex-col shrink-0">
           <nav className="p-4 space-y-2 flex-1">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all group ${
                    activeTab === tab.id
                      ? 'bg-red-500/10 text-red-400 border border-red-500/20 shadow-inner'
                      : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground'
                  }`}
                >
                  <tab.icon className={`w-4 h-4 transition-transform group-hover:scale-110 ${activeTab === tab.id ? tab.color : ''}`} />
                  {tab.label}
                  {tab.id === 'alerts' && alerts.filter(a => !a.resolved).length > 0 && (
                    <span className="ml-auto w-5 h-5 rounded-full bg-red-500 text-white text-[10px] flex items-center justify-center font-bold">
                      {alerts.filter(a => !a.resolved).length}
                    </span>
                  )}
                </button>
              ))}
           </nav>

           <div className="p-6 border-t border-border bg-red-500/5">
              <div className="flex justify-between items-end mb-2">
                 <p className="text-[10px] font-bold uppercase text-red-400 tracking-widest">Global Threat</p>
                 <p className="text-xl font-black text-red-500">{threatLevel}%</p>
              </div>
              <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                 <div 
                   className="h-full bg-red-500 transition-all duration-1000" 
                   style={{ width: `${threatLevel}%` }} 
                 />
              </div>
           </div>
        </div>

        {/* MAIN CONTENT AREA */}
        <div className="flex-1 overflow-y-auto p-8 bg-muted/5">
          
          {/* OVERVIEW TAB */}
          {activeTab === 'overview' && (
            <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                 <SecurityStatCard 
                    icon={ShieldCheck} 
                    label="Posture Score" 
                    value="98/100" 
                    desc="Healthy & Optimized" 
                    color="text-green-400"
                 />
                 <SecurityStatCard 
                    icon={Lock} 
                    label="Encrypted Vaults" 
                    value="12 Active" 
                    desc="Zero leaks detected" 
                    color="text-blue-400"
                 />
                 <SecurityStatCard 
                    icon={ShieldAlert} 
                    label="Threats Blocked" 
                    value="1,402" 
                    desc="In the last 24 hours" 
                    color="text-red-400"
                 />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <PlatformMiniCard label="Facebook" type="facebook" />
                <PlatformMiniCard label="Instagram" type="instagram" />
                <PlatformMiniCard label="LinkedIn" type="linkedin" />
                <PlatformMiniCard label="WhatsApp" type="whatsapp" />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                 <div className="card-gold p-6 bg-card border-red-500/20">
                    <h4 className="font-bold flex items-center gap-2 mb-6">
                       <Activity className="w-5 h-5 text-red-400" /> Real-time Threat Radar
                    </h4>
                    <div className="h-64 flex flex-col items-center justify-center relative">
                       {/* Animated Radar Effect */}
                       <div className="absolute inset-0 flex items-center justify-center">
                          <div className="w-48 h-48 rounded-full border border-red-500/30 animate-ping duration-[3000ms]" />
                          <div className="w-32 h-32 rounded-full border border-red-500/20 animate-ping duration-[2000ms]" />
                          <div className="w-16 h-16 rounded-full border border-red-500/10 animate-ping" />
                       </div>
                       <Shield className="w-16 h-16 text-red-500/40 relative z-10" />
                       <div className="mt-6 text-center z-10">
                          <p className="text-2xl font-black text-foreground">LOW RISK</p>
                          <p className="text-xs text-muted-foreground mt-1">AI Employee is actively shielding your workspace</p>
                       </div>
                    </div>
                 </div>

                 <div className="card-gold p-6 bg-card overflow-hidden">
                    <h4 className="font-bold flex items-center gap-2 mb-6">
                       <Terminal className="w-5 h-5 text-green-400" /> Live Security Feed
                    </h4>
                    <div className="space-y-3 font-mono text-[11px]">
                       {auditLog.slice(0, 8).map((log) => (
                         <div key={log.id} className="flex gap-4 border-b border-border/30 pb-2 last:border-0 group">
                            <span className="text-muted-foreground shrink-0">{log.timestamp}</span>
                            <span className={`${log.status === 'failure' ? 'text-red-400' : 'text-green-400'} shrink-0`}>
                              {log.status === 'success' ? '[PASS]' : '[FAIL]'}
                            </span>
                            <span className="font-bold text-foreground truncate group-hover:text-gold-400 transition-colors">
                              {log.action}
                            </span>
                            <span className="text-muted-foreground ml-auto">{log.ip}</span>
                         </div>
                       ))}
                    </div>
                 </div>
              </div>
            </div>
          )}

          {/* API KEYS TAB */}
          {activeTab === 'keys' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold">API Access Management</h3>
                  <p className="text-sm text-muted-foreground">Manage and rotate your platform access tokens</p>
                </div>
                <button className="btn-primary flex items-center gap-2 py-2">
                  <Zap className="w-4 h-4" /> Generate New Key
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {apiKeys.map(key => (
                  <div key={key.id} className="p-5 rounded-2xl bg-card border border-border hover:border-gold-500/30 transition-all shadow-sm group">
                    <div className="flex items-center justify-between mb-4">
                       <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-lg ${key.status === 'warning' ? 'bg-orange-500/10 text-orange-400' : 'bg-gold-500/10 text-gold-400'}`}>
                             <Key className="w-5 h-5" />
                          </div>
                          <span className="font-bold">{key.name}</span>
                       </div>
                       <span className={`text-[10px] font-bold px-2 py-1 rounded border ${
                         key.status === 'active' ? 'bg-green-500/10 text-green-400 border-green-500/20' : 
                         'bg-orange-500/10 text-orange-400 border-orange-500/20'
                       }`}>
                         {key.status.toUpperCase()}
                       </span>
                    </div>

                    <div className="flex items-center gap-2 mb-4">
                      <div className="flex-1 relative">
                        <input
                          type={showKeys[key.id] ? 'text' : 'password'}
                          value={key.value}
                          readOnly
                          className="w-full pl-4 pr-10 py-3 bg-muted border border-border rounded-xl text-sm font-mono focus:ring-1 ring-gold-500/50 outline-none"
                        />
                        <button 
                          onClick={() => toggleShow(key.id)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground p-1"
                        >
                          {showKeys[key.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                      <button 
                        onClick={() => copyToClipboard(key.value)}
                        className="p-3 bg-muted border border-border rounded-xl hover:bg-gold-500/10 hover:text-gold-400 transition-all"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                       <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          Expires: {key.expires}
                       </div>
                       <div className="flex items-center gap-1">
                          <Activity className="w-3 h-3 text-gold-400" />
                          Last Used: {key.lastUsed}
                       </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SESSIONS TAB */}
          {activeTab === 'sessions' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
               <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold">Active User Sessions</h3>
                  <p className="text-sm text-muted-foreground">Live monitoring of all connected devices and services</p>
                </div>
                <button className="btn-secondary text-red-400 border-red-500/20 hover:bg-red-500/10 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" /> Terminate All
                </button>
              </div>

              <div className="card-gold bg-card overflow-hidden">
                 <table className="w-full text-left">
                    <thead className="bg-muted/50 text-[11px] font-bold uppercase tracking-widest text-muted-foreground">
                       <tr>
                          <th className="px-6 py-4">Device / Identity</th>
                          <th className="px-6 py-4">Location</th>
                          <th className="px-6 py-4">IP Address</th>
                          <th className="px-6 py-4">Activity</th>
                          <th className="px-6 py-4 text-right">Action</th>
                       </tr>
                    </thead>
                    <tbody className="divide-y divide-border/50">
                       {sessions.map(session => (
                         <tr key={session.id} className="hover:bg-muted/30 transition-colors group">
                            <td className="px-6 py-4">
                               <div className="flex items-center gap-3">
                                  <div className={`p-2 rounded-lg ${session.isCurrent ? 'bg-green-500/10 text-green-400' : 'bg-muted text-muted-foreground'}`}>
                                     {session.type === 'desktop' && <Monitor className="w-5 h-5" />}
                                     {session.type === 'mobile' && <Smartphone className="w-5 h-5" />}
                                     {session.type === 'bot' && <Cpu className="w-5 h-5" />}
                                  </div>
                                  <div>
                                     <p className="text-sm font-bold flex items-center gap-2">
                                        {session.device}
                                        {session.isCurrent && <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-green-500 text-white font-bold">CURRENT</span>}
                                     </p>
                                     <p className="text-xs text-muted-foreground">ID: {session.id}</p>
                                  </div>
                               </div>
                            </td>
                            <td className="px-6 py-4">
                               <div className="flex items-center gap-1 text-sm">
                                  <Globe className="w-3.5 h-3.5 text-blue-400" />
                                  {session.location}
                               </div>
                            </td>
                            <td className="px-6 py-4 font-mono text-xs text-muted-foreground">{session.ip}</td>
                            <td className="px-6 py-4">
                               <div className="flex items-center gap-2">
                                  <div className={`w-2 h-2 rounded-full ${session.lastActive === 'Active now' ? 'bg-green-500 animate-pulse' : 'bg-muted-foreground/30'}`} />
                                  <span className="text-xs">{session.lastActive}</span>
                               </div>
                            </td>
                            <td className="px-6 py-4 text-right">
                               {!session.isCurrent && (
                                 <button className="text-xs font-bold text-red-400 hover:underline opacity-0 group-hover:opacity-100 transition-opacity">
                                    Revoke
                                 </button>
                               )}
                            </td>
                         </tr>
                       ))}
                    </tbody>
                 </table>
              </div>
            </div>
          )}

          {/* AUDIT LOG TAB */}
          {activeTab === 'audit' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
               <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-xl font-bold">Immutable Audit Log</h3>
                  <p className="text-sm text-muted-foreground">Tamper-proof history of all system events</p>
                </div>
                <div className="flex gap-2">
                   <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <input 
                        type="text" 
                        placeholder="Search logs..." 
                        className="pl-10 pr-4 py-2 bg-muted border border-border rounded-xl text-xs w-64 outline-none focus:ring-1 ring-gold-500/50"
                      />
                   </div>
                   <button className="p-2 rounded-xl bg-muted border border-border hover:bg-gold-500/10 transition-all">
                      <Filter className="w-4 h-4" />
                   </button>
                </div>
              </div>

              <div className="space-y-3">
                 {auditLog.map(log => (
                   <div key={log.id} className="flex items-center gap-6 p-4 rounded-xl bg-card border border-border hover:border-gold-500/30 transition-all group">
                      <div className={`p-2 rounded-lg ${log.status === 'failure' ? 'bg-red-500/10 text-red-500' : 'bg-green-500/10 text-green-500'}`}>
                         {log.status === 'failure' ? <ShieldAlert className="w-5 h-5" /> : <ShieldCheck className="w-5 h-5" />}
                      </div>
                      
                      <div className="flex-1 grid grid-cols-4 gap-4 items-center">
                         <div>
                            <p className="text-sm font-bold">{log.action}</p>
                            <p className="text-[10px] uppercase text-muted-foreground font-bold tracking-widest">{log.id}</p>
                         </div>
                         <div className="flex items-center gap-2">
                            <User className="w-3.5 h-3.5 text-gold-400" />
                            <span className="text-sm">{log.user}</span>
                         </div>
                         <div className="flex items-center gap-2">
                            <Globe className="w-3.5 h-3.5 text-blue-400" />
                            <span className="text-xs font-mono">{log.ip}</span>
                         </div>
                         <div className="text-right">
                            <span className="text-xs text-muted-foreground">{log.timestamp}</span>
                         </div>
                      </div>

                      <div className={`w-2 h-12 rounded-full ${log.status === 'failure' ? 'bg-red-500' : 'bg-green-500'} opacity-0 group-hover:opacity-100 transition-opacity`} />
                   </div>
                 ))}
              </div>
            </div>
          )}

          {/* ALERTS TAB */}
          {activeTab === 'alerts' && (
             <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
                <div className="flex items-center justify-between">
                   <div>
                     <h3 className="text-xl font-bold">Threat Alerts</h3>
                     <p className="text-sm text-muted-foreground">Active and archived security notifications</p>
                   </div>
                   <button className="text-xs font-bold text-gold-400 hover:underline">Mark all resolved</button>
                </div>

                <div className="space-y-4">
                   {alerts.map(alert => (
                     <div key={alert.id} className={`p-6 rounded-2xl border flex items-start gap-6 bg-card transition-all relative overflow-hidden group ${
                       alert.severity === 'critical' ? 'border-red-500/30 bg-red-500/5' : 
                       alert.severity === 'warning' ? 'border-orange-500/30 bg-orange-500/5' : 
                       'border-blue-500/30 bg-blue-500/5'
                     }`}>
                        {alert.severity === 'critical' && <div className="absolute top-0 left-0 w-1 h-full bg-red-500" />}
                        {alert.severity === 'warning' && <div className="absolute top-0 left-0 w-1 h-full bg-orange-500" />}
                        {alert.severity === 'info' && <div className="absolute top-0 left-0 w-1 h-full bg-blue-500" />}

                        <div className={`p-3 rounded-xl ${
                          alert.severity === 'critical' ? 'bg-red-500/20 text-red-400' : 
                          alert.severity === 'warning' ? 'bg-orange-500/20 text-orange-400' : 
                          'bg-blue-500/20 text-blue-400'
                        }`}>
                           {alert.severity === 'critical' ? <ShieldAlert className="w-6 h-6 animate-pulse" /> : 
                            alert.severity === 'warning' ? <AlertTriangle className="w-6 h-6" /> : 
                            <Bell className="w-6 h-6" />}
                        </div>

                        <div className="flex-1">
                           <div className="flex items-center justify-between mb-1">
                              <span className={`text-[10px] font-black uppercase tracking-widest ${
                                alert.severity === 'critical' ? 'text-red-400' : 
                                alert.severity === 'warning' ? 'text-orange-400' : 
                                'text-blue-400'
                              }`}>
                                {alert.severity} • {alert.source}
                              </span>
                              <span className="text-xs text-muted-foreground">{alert.time}</span>
                           </div>
                           <h4 className="font-bold text-lg mb-1">{alert.message}</h4>
                           <p className="text-sm text-muted-foreground">Action required: Verify source and rotate credentials if necessary.</p>
                           
                           <div className="mt-4 flex gap-3">
                              <button className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
                                alert.severity === 'critical' ? 'bg-red-500 text-white hover:bg-red-600' : 
                                'bg-muted border border-border hover:bg-muted/80'
                              }`}>
                                 Investigate
                              </button>
                              <button className="px-4 py-1.5 rounded-lg text-xs font-bold bg-muted border border-border hover:bg-muted/80">
                                 Dismiss
                              </button>
                           </div>
                        </div>

                        {alert.resolved && (
                          <div className="absolute top-4 right-4 text-green-400 flex items-center gap-1">
                             <CheckCircle className="w-4 h-4" />
                             <span className="text-[10px] font-bold uppercase">Resolved</span>
                          </div>
                        )}
                     </div>
                   ))}
                </div>
             </div>
          )}

        </div>
      </div>

      {/* FOOTER */}
      <div className="px-8 py-4 border-t border-border bg-muted/30 flex items-center justify-between text-[10px] font-bold uppercase tracking-widest text-muted-foreground shrink-0">
         <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
               <ShieldCheck className="w-3.5 h-3.5 text-green-500" />
               Firewall v4.2.0 Active
            </span>
            <span className="flex items-center gap-1.5">
               <Lock className="w-3.5 h-3.5 text-blue-500" />
               AES-256 Protocol Enabled
            </span>
         </div>
         <div className="flex items-center gap-4">
            <span>Last Full Audit: {new Date().toLocaleDateString()}</span>
            <span className="text-red-400">Secure AI Environment</span>
         </div>
      </div>
    </div>
  )
}

/* ================= HELPERS ================= */

function SecurityStatCard({ icon: Icon, label, value, desc, color }: any) {
  return (
    <div className="p-6 rounded-2xl bg-card border border-border shadow-sm flex items-start gap-4">
      <div className={`p-3 rounded-xl bg-muted border border-border ${color}`}>
         <Icon className="w-6 h-6" />
      </div>
      <div>
         <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-1">{label}</p>
         <p className="text-2xl font-black text-foreground mb-1">{value}</p>
         <p className="text-xs text-muted-foreground">{desc}</p>
      </div>
    </div>
  )
}

function PlatformMiniCard({ label, type }: { label: string, type: string }) {
  const [status, setStatus] = useState<'active' | 'inactive' | 'loading'>('loading')

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
        const res = await fetch(`${apiBase}/api/platforms/status`)
        if (res.ok) {
          const data = await res.json()
          setStatus(data[type] === 'active' ? 'active' : 'inactive')
        }
      } catch (e) {
        setStatus('inactive')
      }
    }
    fetchStatus()
  }, [type])

  return (
    <div className="p-3 rounded-xl bg-muted/30 border border-border flex items-center justify-between">
      <span className="text-xs font-bold">{label}</span>
      <div className="flex items-center gap-2">
        <div className={`w-1.5 h-1.5 rounded-full ${
          status === 'active' ? 'bg-green-500 animate-pulse' : 
          status === 'loading' ? 'bg-muted-foreground animate-pulse' : 'bg-red-500'
        }`} />
        <span className={`text-[10px] font-black uppercase ${
          status === 'active' ? 'text-green-400' : 
          status === 'loading' ? 'text-muted-foreground' : 'text-red-400'
        }`}>
          {status}
        </span>
      </div>
    </div>
  )
}
