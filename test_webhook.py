import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('WHATSAPP_ACCESS_TOKEN')
waba_id = os.getenv('WHATSAPP_WABA_ID')

print(f"Token: {token[:20]}...")
print(f"WABA ID: {waba_id}")

r = requests.post(
    f'https://graph.facebook.com/v19.0/{waba_id}/subscribed_apps',
    headers={'Authorization': f'Bearer {token}'}
)
print(r.json())