import requests, os
from dotenv import load_dotenv

load_dotenv('.env', override=True)
admin_num = os.getenv('WHATSAPP_ADMIN_NUMBER', '923491379839').replace('+', '')

draft = """💬 *LinkedIn Comment Reply Draft*

*Original Comment:* "Good to see K-Electric taking these steps for Karachi."

*AI Draft Reply:* "Thank you for your support! We are committed to powering Karachi and continuing our efforts to modernize the grid for a more reliable future."

Reply with *YES* to post this reply on LinkedIn."""

try:
    resp = requests.post('http://localhost:3001/send', json={'number': admin_num, 'message': draft})
    print(f'Status: {resp.status_code}, Body: {resp.text}')
except Exception as e:
    print(f'Error: {e}')
