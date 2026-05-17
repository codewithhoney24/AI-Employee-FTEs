# AI Employee API Version (V3)

This is the production-grade, API-driven architecture for the KE AI Employee.

## V3 Enhancements
- **Robust Parsing**: WhatsApp gateway now captures captions from images/videos and handles extended text formats.
- **Admin Security**: Strict filtering for the Admin number; group messages (`@g.us`) are automatically ignored.
- **Gemini V3 SDK**: Migrated to the new `google-genai` SDK using `gemini-3.1-pro-preview`.
- **Deduplication**: Message queue/ID tracking prevents duplicate command processing.

## Setup
...
### 2. AI Engine (V3)
```bash
cd ai_engine
pip install -r requirements.txt
python app.py
```

## Commands (WhatsApp)
- `generate`: Trigger a new AI draft generation.
- `YES`: Approve and post to Twitter/X.
- `NO`: Cancel the draft.
- `EDIT <text>`: Modify the draft.
- `status`: Check current engine status.

## Requirements
- Node.js 18+
- Python 3.10+
- Twitter API v2 Credentials (set in `.env`)
- Gemini API Key (set in `.env`)
