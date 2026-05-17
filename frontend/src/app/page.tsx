'use client'

import { useState } from 'react'
import Dashboard from '@/components/Dashboard'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import OdooModal from '@/components/OdooModal'
import FacebookModal from '@/components/FacebookModal'
import WhatsAppModal from '@/components/WhatsAppModal'
import GmailModal from '@/components/GmailModal'
import TwitterModal from '@/components/TwitterModal'
import LinkedInModal from '@/components/LinkedInModal'
import SecurityModal from '@/components/SecurityModal'
import { ActivityProvider } from '@/contexts/ActivityContext'
import { ModalType } from '@/types'

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [activeModal, setActiveModal] = useState<ModalType | null>(null)

  return (
    <ActivityProvider>
      <div className="flex h-screen overflow-hidden bg-background text-foreground transition-colors duration-500">
        {/* Sidebar */}
        <Sidebar
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
          onOpenModal={(type) => setActiveModal(type as ModalType)}
        />

        {/* Main Content */}
        <div className={`flex-1 flex flex-col overflow-hidden transition-all duration-300 ${sidebarOpen ? 'ml-0' : 'ml-0'}`}>
          {/* Header */}
          <Header
            sidebarOpen={sidebarOpen}
            onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
            onOpenModal={(type) => setActiveModal(type)}
          />

          {/* Dashboard Content */}
          <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
            <div className="max-w-[1600px] mx-auto">
               <Dashboard onOpenModal={(type) => setActiveModal(type as ModalType)} />
            </div>
          </main>
        </div>
      </div>

      {/* Modals Container with common overlay */}
      {activeModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div 
            className="absolute inset-0 bg-black/60 backdrop-blur-md animate-in fade-in duration-300" 
            onClick={() => setActiveModal(null)} 
          />
          <div className="relative z-10 w-full max-w-4xl max-h-[90vh] overflow-y-auto animate-in zoom-in-95 duration-300">
            {activeModal === 'odoo' && <OdooModal onClose={() => setActiveModal(null)} />}
            {activeModal === 'facebook' && <FacebookModal onClose={() => setActiveModal(null)} />}
            {activeModal === 'whatsapp' && <WhatsAppModal onClose={() => setActiveModal(null)} />}
            {activeModal === 'gmail' && <GmailModal onClose={() => setActiveModal(null)} />}
            {activeModal === 'twitter' && <TwitterModal onClose={() => setActiveModal(null)} />}
            {activeModal === 'linkedin' && <LinkedInModal onClose={() => setActiveModal(null)} />}
            {activeModal === 'security' && <SecurityModal onClose={() => setActiveModal(null)} />}
          </div>
        </div>
      )}
    </ActivityProvider>
  )
}
