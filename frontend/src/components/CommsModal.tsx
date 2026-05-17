import { Mail, Phone } from 'lucide-react'

export default function CommsModal({ type }: { type: 'gmail' | 'whatsapp' }) {
  return (
    <div className="card-gold border-blue-500/30">
      <h3 className="text-lg font-bold flex items-center gap-2">
        {type === 'gmail' ? <Mail className="text-red-400" /> : <Phone className="text-green-400" />}
        {type.toUpperCase()} Watcher Status
      </h3>
      <div className="mt-4 space-y-3">
        <div className="flex justify-between text-sm border-b border-border pb-2">
          <span>Unread Urgent</span>
          <span className="text-gold-400">07</span>
        </div>
        <div className="flex justify-between text-sm border-b border-border pb-2">
          <span>AI Drafted Replies</span>
          <span className="text-blue-400">04</span>
        </div>
        <div className="p-3 bg-muted/30 rounded text-xs italic">
          &quot;AI is currently scanning for keywords: &apos;bill&apos;, &apos;outage&apos;, &apos;payment&apos;...&quot;
        </div>
      </div>
    </div>
  )
}
