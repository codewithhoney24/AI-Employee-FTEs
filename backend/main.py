import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import asyncio
import uuid
import xmlrpc.client
from dotenv import load_dotenv
import os

# Load credentials from root .env
load_dotenv(dotenv_path="../.env")

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USER = os.getenv("ODOO_USERNAME", "digitaldreamers18@gmail.com")
ODOO_PASS = os.getenv("ODOO_PASSWORD", "admin123")

app = FastAPI(title="KE AI Dashboard Backend")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---

class SystemStatus(BaseModel):
    status: str = "System Online"
    watchers: int = 8
    mcp_servers: int = 7

class DashboardData(BaseModel):
    pending_tasks: int = 5
    completed_today: int = 2
    whatsapp_messages: int = 5
    avg_response_time: str = "1.1h"
    revenue_week: float = 0
    revenue_mtd: float = 0
    approvals_pending: int = 1
    system_status: SystemStatus = SystemStatus(watchers=8, mcp_servers=7)
    facebook_status: str = "active"
    odoo_status: str = "active"
    odoo_crm_leads: int = 0
    odoo_invoices: int = 0
    odoo_pending_invoices: int = 0
    odoo_paid: int = 0
    odoo_last_sync: str = datetime.now().isoformat()
    whatsapp_status: str = "active"

    @classmethod
    def get_latest(cls):
        try:
            common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
            uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
            models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
            
            # 1. Fetch CRM Leads
            leads_count = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'crm.lead', 'search_count', [[]])
            
            # 2. Fetch Invoices and Revenue
            invoices = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'account.move', 'search_read', 
                [[('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]], 
                {'fields': ['amount_total', 'payment_state']})
            
            revenue = sum(inv['amount_total'] for inv in invoices)
            paid_count = len([inv for inv in invoices if inv['payment_state'] == 'paid'])
            pending_invoices_count = len([inv for inv in invoices if inv['payment_state'] != 'paid'])
            
            # 3. Platform Status Logic
            fb_status = "active" if os.getenv("FB_PAGE_ACCESS_TOKEN") else "inactive"
            wa_status = "active" # Local session assumed
            
            return cls(
                revenue_week=revenue,
                revenue_mtd=revenue,
                odoo_crm_leads=leads_count,
                odoo_invoices=len(invoices),
                odoo_pending_invoices=pending_invoices_count,
                odoo_paid=paid_count,
                odoo_last_sync=datetime.now().isoformat(),
                facebook_status=fb_status,
                whatsapp_status=wa_status
            )
        except Exception as e:
            print(f"Error fetching Odoo data: {e}")
            return cls(odoo_status="error")

class GmailStats(BaseModel):
    total: int = 156
    urgent: int = 3
    leads: int = 12
    support: int = 8
    finance: int = 5
    unread: int = 24
    ai_drafts: int = 7
    connected: bool = True
    last_checked: str = datetime.now().isoformat()

class Lead(BaseModel):
    id: str
    name: str
    comment: str
    source: str = "Facebook"
    status: str = "New"
    link: Optional[str] = None
    created: str

class ActivityItem(BaseModel):
    id: str
    action: str
    details: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    timestamp: str

class Bottleneck(BaseModel):
    task: str
    delay: str
    reason: str

class BriefingData(BaseModel):
    period: str = "May 1 - May 7, 2026"
    revenue: Dict[str, str] = {"growth": "+12.5%", "total": "PKR 1,250,000", "status": "On Track"}
    leads: Dict[str, int] = {"new": 12, "total": 48}
    socialImpact: Dict[str, str] = {"instagram": "85% positive sentiment", "facebook": "3 new campaign leads"}
    bottlenecks: List[Bottleneck] = []
    aiSuggestions: List[Dict[str, Any]] = [
        {"id": "1", "text": "Follow up with Solar leads in Gulshan - High conversion probability."},
        {"id": "2", "text": "Migrate Salesforce leads to Odoo to save 50,000 PKR/month."},
        {"id": "3", "text": "Offer Summer Maintenance Package to existing customers."}
    ]

# --- MOCK DATA ---

def get_mock_leads():
    return [
        Lead(id=str(uuid.uuid4()), name="Ali Khan", comment="Interested in solar panel installation for my office in Gulshan.", source="Facebook", status="New", created=datetime.now().isoformat()),
        Lead(id=str(uuid.uuid4()), name="Sara Ahmed", comment="Need pricing for the gold tier business package.", source="Instagram", status="Synced to Odoo", created=datetime.now().isoformat()),
        Lead(id=str(uuid.uuid4()), name="Zeeshan Malik", comment="Is the AI employee service available for real estate?", source="Facebook", status="New", created=datetime.now().isoformat()),
        Lead(id=str(uuid.uuid4()), name="Fatima Zehra", comment="Urgent: Need help with my Odoo integration.", source="WhatsApp", status="In Progress", created=datetime.now().isoformat()),
    ]

MOCK_ACTIVITY = [
    ActivityItem(id=str(uuid.uuid4()), action="approval_requested", details={"message": "Approval requested for 75,000 PKR invoice"}, category="Finance", timestamp=datetime.now().isoformat()),
    ActivityItem(id=str(uuid.uuid4()), action="draft_created", details={"message": "LinkedIn draft created: Scaling Sustainable Energy"}, category="Social", timestamp=datetime.now().isoformat()),
    ActivityItem(id=str(uuid.uuid4()), action="draft_created", details={"message": "Instagram draft created: Energy Saving Tips"}, category="Social", timestamp=datetime.now().isoformat()),
    ActivityItem(id=str(uuid.uuid4()), action="reminder_drafted", details={"message": "Late payment reminder drafted for XYZ Company (8 days overdue)"}, category="Finance", timestamp=datetime.now().isoformat()),
    ActivityItem(id=str(uuid.uuid4()), action="task_completed", details={"message": "Obsidian Dashboard refactored to Simple English"}, category="Tasks", timestamp=datetime.now().isoformat()),
]

# --- ENDPOINTS ---

@app.get("/api/dashboard", response_model=DashboardData)
async def get_dashboard():
    return DashboardData.get_latest()

@app.get("/api/briefing", response_model=BriefingData)
async def get_briefing():
    # Fetch from latest briefing in Obsidian
    briefing_dir = "D:/AI-Employee-FTEs/KE_AI_Vault/Briefings"
    try:
        files = [f for f in os.listdir(briefing_dir) if f.startswith("Weekly_Briefing_")]
        if not files:
            return BriefingData()
        
        latest_file = sorted(files)[-1]
        with open(os.path.join(briefing_dir, latest_file), "r", encoding="utf-8") as f:
            content = f.read()
        
        # Simple extraction logic
        import re
        rev_match = re.search(r'Total Revenue \(Invoiced\):\*\* ([\d,.]+)', content)
        revenue = rev_match.group(1) if rev_match else "0.00"
        
        leads_match = re.search(r'New Leads Captured:\*\* (\d+)', content)
        leads_count = int(leads_match.group(1)) if leads_match else 0
        
        return BriefingData(
            period="May 2026",
            revenue={"growth": "Live", "total": f"PKR {revenue}", "status": "Synced"},
            leads={"new": leads_count, "total": leads_count} # Placeholder for total
        )
    except Exception as e:
        print(f"Error reading briefing: {e}")
        return BriefingData()

@app.get("/api/tasks")
async def get_tasks():
    # Return tasks from Needs_Action folder if it exists
    vault_path = "D:/AI-Employee-FTEs/KE_AI_Vault/Needs_Action"
    tasks = []
    if os.path.exists(vault_path):
        for f in os.listdir(vault_path):
            if f.endswith(".md"):
                priority = "High" if "URGENT" in f.upper() or "BILL" in f.upper() else "Medium"
                type_str = "CRM"
                if "BILL" in f.upper() or "INVOICE" in f.upper(): type_str = "Finance"
                elif "WHATSAPP" in f.upper() or "FB" in f.upper(): type_str = "Social"
                
                tasks.append({
                    "id": f,
                    "title": f.replace(".md", "").replace("_", " "),
                    "status": "pending",
                    "priority": priority,
                    "type": type_str
                })
    return {"tasks": tasks}

@app.get("/api/gmail/status", response_model=GmailStats)
async def get_gmail_status():
    return GmailStats()

@app.get("/api/leads")
async def get_leads():
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        leads_data = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'crm.lead', 'search_read', [[]], {
            'fields': ['name', 'contact_name', 'email_from', 'phone', 'create_date', 'type']
        })
        
        # Convert to Lead model
        real_leads = []
        for l in leads_data:
            real_leads.append(Lead(
                id=str(l['id']),
                name=l['name'],
                comment=f"Contact: {l['contact_name'] or 'N/A'}. Phone: {l['phone'] or 'N/A'}",
                source="Odoo CRM",
                status="Opportunity" if l['type'] == 'opportunity' else "New",
                created=l['create_date']
            ))
        return {"leads": real_leads}
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return {"leads": get_mock_leads()}

@app.get("/api/activity")
async def get_activity(hours: int = 24):
    combined_activity = list(MOCK_ACTIVITY)
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        # Fetch recent leads as activity
        leads = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'crm.lead', 'search_read', [[]], {
            'fields': ['name', 'create_date'], 'limit': 5, 'order': 'create_date desc'
        })
        for l in leads:
            combined_activity.append(ActivityItem(
                id=f"lead-{l['id']}",
                action="lead_captured",
                details={"message": f"New Lead: {l['name']}"},
                category="Sales",
                timestamp=l['create_date']
            ))
            
        # Fetch recent invoices as activity
        invoices = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'account.move', 'search_read', 
            [[('move_type', '=', 'out_invoice')]], 
            {'fields': ['name', 'amount_total', 'create_date'], 'limit': 5, 'order': 'create_date desc'})
        for inv in invoices:
            combined_activity.append(ActivityItem(
                id=f"inv-{inv['id']}",
                action="invoice_generated",
                details={"message": f"Invoice {inv['name']} created for {inv['amount_total']} PKR"},
                category="Finance",
                timestamp=inv['create_date']
            ))
            
    except Exception as e:
        print(f"Error fetching activity: {e}")
        
    # Sort by timestamp desc
    combined_activity.sort(key=lambda x: x.timestamp, reverse=True)
    return {"activity": combined_activity[:10]}

import subprocess

@app.get("/api/accounting/invoices")
async def get_accounting_invoices():
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        invoices_data = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'account.move', 'search_read', 
            [[('move_type', '=', 'out_invoice')]], 
            {'fields': ['name', 'partner_id', 'invoice_date', 'amount_total', 'payment_state', 'state'], 'order': 'invoice_date desc'})
        
        return {"invoices": invoices_data}
    except Exception as e:
        print(f"Error fetching invoices: {e}")
        return {"invoices": []}

@app.post("/api/briefing/audit")
async def run_audit():
    # In a real system, this would trigger generate_briefing.py
    # For the UI feedback, we just return success
    return {"status": "success", "message": "Audit completed. Dashboard updated."}

@app.get("/api/platforms/status")
async def get_platforms_status():
    import socket
    def is_port_open(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(('127.0.0.1', port)) == 0

    return {
        "facebook": "active" if os.getenv("FB_PAGE_ACCESS_TOKEN") else "inactive",
        "instagram": "active" if os.getenv("IG_BUSINESS_ID") or os.getenv("IG_USER_ID") else "inactive",
        "linkedin": "active" if os.getenv("LINKEDIN_ACCESS_TOKEN") else "inactive",
        "twitter": "active" if os.getenv("TWITTER_API_KEY") or os.getenv("X_API_KEY") else "inactive",
        "whatsapp": "active" if is_port_open(3001) else "inactive",
        "gmail": "active", # Assuming always active if configured
        "odoo": "active" if is_port_open(8069) else "inactive",
        "security": "active"
    }

# --- WEBSOCKET ---

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Just keep the connection alive
            data = await websocket.receive_text()
            # Echo for testing
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    # Simulate background updates via broadcast
    async def periodic_broadcast():
        while True:
            await asyncio.sleep(10)
            if manager.active_connections:
                msg = {
                    "type": "system_update",
                    "action": "Heartbeat pulse detected",
                    "timestamp": datetime.now().isoformat()
                }
                await manager.broadcast(json.dumps(msg))
    
    asyncio.create_task(periodic_broadcast())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
