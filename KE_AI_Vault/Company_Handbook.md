# K-Electric Company Handbook (AI Rules)

## Social Media Posting Rules

### LinkedIn (Professional + B2B)
- **Frequency**: 2 posts per day (10 AM, 4 PM)
- **Content Types**: 
  - Infrastructure updates ("نیا power line installed")
  - Business announcements
  - Industry insights
  - Customer success stories
- **Example**: "K-Electric نے Karachi میں 150MW نیا سولر power شامل کیا۔ سبز توانائی کا مستقبل!"
- **Tone**: Professional, optimistic
- **Auto-post**: Yes (with approval)

### Facebook (Customer Service)
- **Frequency**: 3-4 posts per day
- **Content Types**:
  - Grid status updates
  - Bill payment reminders
  - Customer service queries (replies to comments)
  - Load shedding notifications
- **Example**: "گرم خیر مقدم! اگر آپ کو electricity کی شکایت ہے تو یہاں رابطہ کریں: 118"
- **Tone**: Friendly, helpful
- **Auto-reply**: Yes for FAQ questions
- **Requires Approval**: For criticism or complaints

### Instagram (Visual + Marketing)
- **Frequency**: 1-2 posts per day
- **Content Types**:
  - Infographics (بجلی بچانے کے طریقے)
  - Team photos
  - Power infrastructure photos
  - Energy conservation tips
- **Auto-post**: Yes

### Twitter/X (Real-Time Updates)
- **Frequency**: 4-5 tweets per day
- **Content**: 
  - Real-time grid status
  - Load shedding schedule
  - Emergency alerts
  - Industry news
- **Auto-tweet**: Yes for scheduled content
- **Immediate**: No (manual for crisis)

---

## Customer Response Rules

### Email Replies
- **Standard Query**: Auto-generate draft (requires approval)
- **Billing Question**: Auto-generate from /Accounting/
- **Complaint**: Flag as URGENT, create approval file
- **Late Payment Reminder**: Auto-send after 5 days late
- **Response Time**: Max 24 hours

### WhatsApp Responses
- **Keywords to Monitor**: 
  - "bill" / "invoice" → Share billing info
  - "complaint" / "problem" → Create ticket
  - "payment" → Share payment methods
  - "urgent" / "asap" → Mark HIGH priority
- **Response Time**: Within 2 hours (business hours)
- **Auto-reply**: Yes for FAQ
- **Approval**: For any financial commitments

---

## Payment & Billing Rules

### Invoice Generation
- **Threshold**: All invoices auto-generated
- **Approval Required**: If > 50,000 PKR or new customer
- **Auto-send**: Yes via email MCP

### Payment Processing
- **Amount < 10,000 PKR**: Auto-approve with email receipt
- **Amount 10K - 100K**: Requires approval before processing
- **Amount > 100K**: Requires senior approval
- **Late Payments**: Auto-send reminder after 5 days

### Accounting Rules
- **Daily**: Log all transactions to /Accounting/
- **Weekly**: Generate revenue report
- **Monthly**: Reconcile bank statements
- **Quarterly**: Tax audit preparation

---

## Escalation & Error Handling

### When AI Gets Uncertain
- Flag the file to /Pending_Approval/
- Never guess on financial matters
- Always include context for human decision

### Error Scenarios
- **Network timeout**: Retry after 5 minutes (max 3x)
- **API rate limit**: Queue for next hour
- **Authentication error**: Alert human immediately
- **Suspicious activity**: Flag to /Rejected/, alert admin

---

## Daily Checklist (Automated)

✓ Process all /Needs_Action files
✓ Generate social media posts
✓ Send invoice reminders
✓ Update Dashboard.md
✓ Log all actions
✓ Generate weekly briefing (Sundays)
✓ Reconcile transactions (Fridays)
