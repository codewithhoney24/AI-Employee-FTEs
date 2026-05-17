import xmlrpc.client
import os
import logging
from dotenv import load_dotenv

load_dotenv()

class OdooSkill:
    def __init__(self):
        self.url = os.getenv("ODOO_URL", "http://localhost:8069")
        self.db = os.getenv("ODOO_DB", "odoo")
        self.username = os.getenv("ODOO_USERNAME", "admin")
        self.password = os.getenv("ODOO_PASSWORD", "admin")
        self.uid = None
        self._authenticate()

    def _authenticate(self):
        try:
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            return self.uid
        except Exception as e:
            print(f"Odoo Auth Error: {e}")
            return None

    def get_revenue_summary(self):
        """Fetch total revenue and pending payments"""
        if not self.uid: return "Error: Odoo Auth Failed"
        try:
            models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            invoices = models.execute_kw(self.db, self.uid, self.password, 'account.move', 'search_read', 
                [[('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]], 
                {'fields': ['amount_total', 'payment_state']})
            
            total_revenue = sum(inv['amount_total'] for inv in invoices)
            pending = sum(inv['amount_total'] for inv in invoices if inv['payment_state'] != 'paid')
            
            return {
                "total_revenue": total_revenue,
                "pending_payments": pending,
                "count": len(invoices)
            }
        except Exception as e:
            return f"Odoo Error: {e}"

    def create_invoice(self, partner_name, amount, description="AI Generated Service"):
        """Create a draft invoice in Odoo"""
        if not self.uid: return None
        try:
            models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            
            # 1. Find or create partner
            partners = models.execute_kw(self.db, self.uid, self.password, 'res.partner', 'search_read', [[('name', '=', partner_name)]], {'fields': ['id'], 'limit': 1})
            if partners:
                partner_id = partners[0]['id']
            else:
                partner_id = models.execute_kw(self.db, self.uid, self.password, 'res.partner', 'create', [{'name': partner_name}])

            # 2. Create invoice
            invoice_id = models.execute_kw(self.db, self.uid, self.password, 'account.move', 'create', [{
                'partner_id': partner_id,
                'move_type': 'out_invoice',
                'invoice_line_ids': [(0, 0, {
                    'name': description,
                    'quantity': 1,
                    'price_unit': amount,
                })]
            }])
            return invoice_id
        except Exception as e:
            print(f"Invoice Error: {e}")
            return None

if __name__ == "__main__":
    odoo = OdooSkill()
    print(odoo.get_revenue_summary())
