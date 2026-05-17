export default function PGAdminModal({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="card-gold max-w-4xl w-full p-6">
        <h2 className="text-xl font-bold mb-4">Cloud Database Explorer</h2>
        <p className="text-sm mb-6">Secure access to the KE AI Vault database.</p>
        <button onClick={onClose} className="btn-secondary w-full">Close Explorer</button>
      </div>
    </div>
  )
}
