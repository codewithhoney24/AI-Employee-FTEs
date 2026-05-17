import os
import json
import sys
import xmlrpc.client
from dotenv import load_dotenv

# Load Odoo credentials from .env
load_dotenv()

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "ke_gold_db")
ODOO_USER = os.getenv("ODOO_USER", "admin")
ODOO_PASS = os.getenv("ODOO_PASS", "your_secure_password")

def get_odoo_connection():
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
        if not uid:
            return None, "Authentication failed"
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        return (uid, models), None
    except Exception as e:
        return None, str(e)

def list_leads():
    conn, error = get_odoo_connection()
    if error: return {"error": error}
    uid, models = conn
    leads = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'crm.lead', 'search_read', [[]], {'fields': ['name', 'contact_name', 'email_from', 'phone', 'expected_revenue']})
    return leads

def create_lead(name, contact_name=None, email=None, phone=None):
    conn, error = get_odoo_connection()
    if error: return {"error": error}
    uid, models = conn
    lead_id = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'crm.lead', 'create', [{
        'name': name,
        'contact_name': contact_name,
        'email_from': email,
        'phone': phone
    }])
    return {"lead_id": lead_id}

def list_invoices():
    conn, error = get_odoo_connection()
    if error: return {"error": error}
    uid, models = conn
    invoices = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'account.move', 'search_read', [[('move_type', '=', 'out_invoice')]], {'fields': ['name', 'partner_id', 'amount_total', 'payment_state']})
    return invoices

def handle_mcp_request(request):
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "list_leads":
        return list_leads()
    elif method == "create_lead":
        return create_lead(**params)
    elif method == "list_invoices":
        return list_invoices()
    else:
        return {"error": f"Method {method} not found"}

if __name__ == "__main__":
    # Simple JSON-RPC over stdin/stdout for MCP
    for line in sys.stdin:
        try:
            request = json.loads(line)
            response = handle_mcp_request(request)
            print(json.dumps({"id": request.get("id"), "result": response}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
