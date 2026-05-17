'use client'

import React from 'react'
import { Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'

interface RevenueChartProps {
  data?: Array<{
    day: string
    revenue: number
    target: number
  }>
}

export default function RevenueChart({ data }: RevenueChartProps) {
  const chartData = data || [
    { day: 'Mon', revenue: 1200, target: 1500 },
    { day: 'Tue', revenue: 2100, target: 1500 },
    { day: 'Wed', revenue: 1800, target: 1500 },
    { day: 'Thu', revenue: 2400, target: 1500 },
    { day: 'Fri', revenue: 3200, target: 1500 },
    { day: 'Sat', revenue: 2800, target: 1500 },
    { day: 'Sun', revenue: 1900, target: 1500 },
  ]

  return (
    <div className="w-full h-full min-h-[300px]">
      <ResponsiveContainer width="100%" height="100%" minWidth={0}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f7941e" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#f7941e" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis 
            dataKey="day" 
            stroke="hsl(var(--muted-foreground))"
            tick={{ fill: 'hsl(var(--muted-foreground))' }}
          />
          <YAxis 
            stroke="hsl(var(--muted-foreground))"
            tick={{ fill: 'hsl(var(--muted-foreground))' }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'hsl(var(--card))', 
              border: '1px solid hsl(var(--border))',
              borderRadius: '8px',
              backdropFilter: 'blur(10px)'
            }} 
            labelStyle={{ color: 'hsl(var(--foreground))' }}
            itemStyle={{ color: 'hsl(var(--gold-400))' }}
          />
          <Area 
            type="monotone" 
            dataKey="revenue" 
            stroke="#f7941e" 
            strokeWidth={3}
            fillOpacity={1} 
            fill="url(#colorRevenue)"
            className="animate-fade-in"
          />
          <Line 
            type="monotone" 
            dataKey="target" 
            stroke="#22c55e" 
            strokeWidth={2}
            strokeDasharray="5 5"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
