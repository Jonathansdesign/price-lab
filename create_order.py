import os
import requests
from dotenv import load_dotenv

"""
Collects money from a buyer into (your) Business
Account. In Tanda, this would be a member's monthly 
contribution.
"""
load_dotenv()
CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
BASE = "https://api-m.sandbox.paypal.com"

# Step 1: exchange your keys for an access token
token_resp = requests.post(
    f"{BASE}/v1/oauth2/token",
    auth=(CLIENT_ID, CLIENT_SECRET),
    data={"grant_type": "client_credentials"},
)
token_resp.raise_for_status()
token = token_resp.json()["access_token"]
print("Got access token")

# Step 2: create an order for a candle priced at $12.00
order_resp = requests.post(
    f"{BASE}/v2/checkout/orders",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "intent": "CAPTURE",
        "purchase_units": [
            {"amount": {"currency_code": "USD", "value": "12.00"}}
        ],
    },
)
order_resp.raise_for_status()
order = order_resp.json()

print("Order ID:", order["id"])
print("Status:", order["status"])
for link in order["links"]:
    if link["rel"] == "approve":
        print("Buyer approval link:", link["href"])