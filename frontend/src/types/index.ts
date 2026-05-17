export interface Notification {
  id: string
  title: string
  desc: string
  time: string
  read: boolean
  type: 'lead' | 'payment' | 'task' | 'alert' | 'social'
  action?: string
}

export type ModalType = 'odoo' | 'facebook' | 'whatsapp' | 'gmail' | 'twitter' | 'linkedin' | 'security'
