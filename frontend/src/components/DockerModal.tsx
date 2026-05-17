'use client'

import React from 'react'
import { X, Zap, Server, Database, Terminal, CheckCircle } from 'lucide-react'
import useSWR from 'swr'

interface DockerModalProps {
  onClose: () => void
  onOpenExplorer?: () => void
}

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export default function DockerModal({ onClose, onOpenExplorer }: DockerModalProps) {
  const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'
  const { data: dockerStatus } = useSWR(`${apiBase}/api/docker/status`, fetcher, {
    refreshInterval: 10000
  })

  const containers = [
    { 
      name: 'Local Odoo (Web)', 
      image: 'odoo:17.0', 
      status: dockerStatus?.odoo || 'running', 
      port: '8069', 
      icon: Server, 
      color: 'purple' 
    },
    { 
      name: 'Local PostgreSQL', 
      image: 'postgres:15', 
      status: dockerStatus?.postgres || 'running', 
      port: '5432', 
      icon: Database, 
      color: 'blue' 
    },
    { 
      name: 'AI MCP Bridge', 
      image: 'Gold Tier Orchestrator', 
      status: 'running', 
      port: '8000', 
      icon: Zap, 
      color: 'gold' 
    },
  ]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-4xl max-h-[90vh] overflow-auto rounded-2xl bg-card border border-border shadow-2xl animate-fade-in">
        {/* Header */}
        <div className="sticky top-0 flex items-center justify-between border-b border-border bg-card p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/20">
              <Zap className="h-6 w-6 text-blue-400" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Infrastructure Status</h2>
              <p className="text-sm text-muted-foreground">AI Employee Gold Tier - Local Docker Ecosystem</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-2 hover:bg-muted transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Container Status */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {containers.map((container, i) => (
              <div key={i} className={`rounded-xl border p-4 ${
                container.status === 'healthy' ? 'border-green-500/30 bg-green-500/10' :
                container.status === 'running' ? 'border-blue-500/30 bg-blue-500/10' :
                'border-red-500/30 bg-red-500/10'
              }`}>
                <div className="flex items-center justify-between mb-3">
                  <container.icon className={`w-8 h-8 ${
                    container.color === 'blue' ? 'text-blue-400' :
                    container.color === 'purple' ? 'text-purple-400' :
                    'text-gold-400'
                  }`} />
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      container.status === 'healthy' ? 'bg-green-500' :
                      container.status === 'running' ? 'bg-blue-500' :
                      'bg-red-500'
                    }`} />
                    <span className={`text-xs font-medium ${
                      container.status === 'healthy' ? 'text-green-400' :
                      container.status === 'running' ? 'text-blue-400' :
                      'text-red-400'
                    }`}>
                      {container.status}
                    </span>
                  </div>
                </div>
                <h3 className="font-semibold text-sm mb-1">{container.name}</h3>
                <p className="text-xs text-muted-foreground mb-3">{container.image}</p>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Port: {container.port}</span>
                  {container.status === 'healthy' && <CheckCircle className="w-4 h-4 text-green-400" />}
                </div>
              </div>
            ))}
          </div>

          {/* Commands */}
          <div className="rounded-xl border border-border bg-card">
            <div className="border-b border-border p-4">
              <h3 className="text-lg font-semibold">Terminal Commands</h3>
            </div>
            <div className="p-4 space-y-2">
              {[
                { cmd: 'docker ps', desc: 'List running containers' },
                { cmd: 'docker-compose logs odoo', desc: 'View Odoo logs' },
                { cmd: 'docker-compose down -v', desc: 'Stop and remove all containers' },
                { cmd: 'docker-compose up -d --build', desc: 'Rebuild and start containers' },
              ].map((item, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-muted/50 border border-border">
                  <Terminal className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-mono text-sm text-gold-400">{item.cmd}</p>
                    <p className="text-xs text-muted-foreground">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Architecture */}
          <div className="rounded-xl border border-border bg-card">
            <div className="border-b border-border p-4">
              <h3 className="text-lg font-semibold">Local-First Infrastructure</h3>
            </div>
            <div className="p-4">
              <div className="space-y-3">
                <div className="flex items-center gap-4 p-3 rounded-lg bg-blue-500/10 border border-blue-500/30">
                  <Database className="w-6 h-6 text-blue-400" />
                  <div className="flex-1">
                    <p className="font-medium">Local PostgreSQL (Docker)</p>
                    <p className="text-xs text-muted-foreground">Port: 5432 | Primary Database</p>
                  </div>
                </div>
                <div className="flex justify-center"><Server className="w-5 h-5 text-muted-foreground" /></div>
                <div className="flex items-center gap-4 p-3 rounded-lg bg-purple-500/10 border border-purple-500/30">
                  <Server className="w-6 h-6 text-purple-400" />
                  <div className="flex-1">
                    <p className="font-medium">Local Odoo (Docker)</p>
                    <p className="text-xs text-muted-foreground">Port: 8069 | Business ERP</p>
                  </div>
                </div>
                <div className="flex justify-center"><Zap className="w-5 h-5 text-muted-foreground" /></div>
                <div className="flex items-center gap-4 p-3 rounded-lg bg-gold-500/10 border border-gold-500/30">
                  <Zap className="w-6 h-6 text-gold-400" />
                  <div className="flex-1">
                    <p className="font-medium">Gold Tier Orchestrator</p>
                    <p className="text-xs text-muted-foreground">AI Integration & Python Backend</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
