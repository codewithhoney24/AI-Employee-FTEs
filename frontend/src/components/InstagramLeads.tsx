import { Camera } from 'lucide-react'
 
export default function InstagramLeads() {
  const leads = [
    { user: "@ali_khan", comment: "Interested in Solar installation", status: "Detected" },
    { user: "@tech_khi", comment: "What is the commercial unit rate?", status: "Replied" }
  ];

  return (
    <div className="card-gold border-pink-500/30">
      <h3 className="text-pink-400 font-bold mb-3 flex items-center gap-2">
        <Camera className="w-5 h-5" /> Instagram Lead Detector
      </h3>
      <div className="space-y-2">
        {leads.map((l, i) => (
          <div key={i} className="flex justify-between items-center text-xs p-2 bg-muted/50 rounded">
            <div>
              <span className="font-bold">{l.user}</span>
              <p className="text-muted-foreground">{l.comment}</p>
            </div>
            <span className="badge-gold text-[10px]">{l.status}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
