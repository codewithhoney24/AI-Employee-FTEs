'use client'

import React from 'react'
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface MetricCardProps {
  title: string
  value: string | number
  change?: number
  changeType?: 'increase' | 'decrease' | 'neutral'
  icon: LucideIcon
  color?: 'gold' | 'green' | 'blue' | 'purple' | 'red'
  size?: 'normal' | 'large'
}

export default function MetricCard({
  title,
  value,
  change,
  changeType = 'neutral',
  icon: Icon,
  color = 'gold',
  size = 'normal'
}: MetricCardProps) {
  
  const iconColorClasses = {
    gold: 'text-gold-400 bg-gold-500/20',
    green: 'text-green-400 bg-green-500/20',
    blue: 'text-blue-400 bg-blue-500/20',
    purple: 'text-purple-400 bg-purple-500/20',
    red: 'text-red-400 bg-red-500/20'
  }

  return (
    <div className={`card-gold p-6 flex flex-col justify-between hover:scale-[1.02] transition-transform duration-300 ${size === 'large' ? 'h-48' : 'h-40'}`}>
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-xl ${iconColorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        {change !== undefined && (
          <div className={`flex items-center gap-1 text-xs font-bold px-2 py-1 rounded-full ${
            changeType === 'increase' ? 'text-green-400 bg-green-500/10' :
            changeType === 'decrease' ? 'text-red-400 bg-red-500/10' :
            'text-muted-foreground bg-muted'
          }`}>
            {changeType === 'increase' && <TrendingUp className="w-3 h-3" />}
            {changeType === 'decrease' && <TrendingDown className="w-3 h-3" />}
            {changeType === 'neutral' && <Minus className="w-3 h-3" />}
            {change}%
          </div>
        )}
      </div>
      <div>
        <p className="text-sm text-muted-foreground font-medium mb-1 uppercase tracking-wider">{title}</p>
        <p className={`font-bold ${size === 'large' ? 'text-3xl' : 'text-2xl'}`}>{value}</p>
      </div>
    </div>
  )
}
