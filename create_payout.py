import os
import time
import requests
from dotenv import load_dotenv

"""
Sends money out of Business account to a recipient.
In Tanda, this is the round winner's payout.
"""

load_dotenv()
CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
RECEIVER = os.getenv("PAYPAL_TEST_RECEIVER")
BASE = "https://api-m.sandbox.paypal.com"

token_resp = requests.post(
    f"{BASE}/v1/oauth2/token",
    auth=(CLIENT_ID, CLIENT_SECRET),
    data={"grant_type": "client_credentials"},
)
token_resp.raise_for_status()
token = token_resp.json()["access_token"]

body = {
    "sender_batch_header": {
        "sender_batch_id": f"tanda-test-{int(time.time())}",
        "email_subject": "Tanda test payout",
        "email_message": "Sandbox test payout",
    },
    "items": [
        {
            "recipient_type": "EMAIL",
            "amount": {"value": "5.00", "currency": "USD"},
            "receiver": RECEIVER,
            "note": "Round 1 payout",
            "sender_item_id": "round-1",
        }
    ],
}

resp = requests.post(
    f"{BASE}/v1/payments/payouts",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json=body,
)
print("HTTP status:", resp.status_code)
print(resp.json())