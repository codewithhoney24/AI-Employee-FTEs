# Project Instructions: K-Electric AI Employee

## Architecture Shift (May 2026 - V3 Upgrade)
The system has been upgraded to **V3** for enhanced stability:
- **WhatsApp**: Using `@whiskeysockets/baileys` with robust message parsing (captions, extended text).
- **Twitter**: Official Twitter API v2 via `tweepy`.
- **AI Brain**: Upgraded to the new **Google GenAI SDK** (`google-genai`) using `gemini-3.1-pro-preview`.
- **Security**: Strict Admin filtering and message deduplication.

## Conventions
- **API-First**: Prefer using official APIs or lightweight libraries (like Baileys) over browser automation.
- **Human-in-the-Loop**: All automated posts must be approved via WhatsApp with a "YES" command.
- **Secrets**: Store all credentials in `.env` files. Do NOT hardcode keys.
- **Communication**: The Node.js WhatsApp gateway communicates with the Python AI engine via HTTP webhooks on `localhost:5000`.

## Directory Structure
- `api_employee_v2/whatsapp_gateway`: Node.js server for WhatsApp.
- `api_employee_v2/ai_engine`: Python/Flask server for AI logic and Twitter posting.
- `KE_AI_Vault/`: Obsidian vault for memory and legacy script support.

## Security
- Always verify the sender's phone number in WhatsApp webhooks to ensure only authorized admins can issue commands.
