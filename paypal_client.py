"""Small PayPal sandbox client used by Tanda.

Every PayPal call in the project goes through this class.
Rest of the code never repeats token or error handling.
"""

import os
import time
import uuid

import requests
from dotenv import load_dotenv

load_dotenv()

BASE = "https://api-m.sandbox.paypal.com"  # sandbox only: no actual money


class PayPalError(Exception):
    """Raised when PayPal returns an error. Includes the debug_id PayPal asks for in support tickets."""


class PayPalClient:
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id or os.getenv("PAYPAL_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("PAYPAL_CLIENT_SECRET")
        if not self.client_id or not self.client_secret:
            raise PayPalError("Missing PAYPAL_CLIENT_ID or PAYPAL_CLIENT_SECRET in .env")
        self._token = None
        self._expires_at = 0.0

    # ---- authentication (token is reused until shortly before it expires) ----
    def _get_token(self):
        if self._token and time.time() < self._expires_at:
            return self._token
        resp = requests.post(
            f"{BASE}/v1/oauth2/token",
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"},
            timeout=30,
        )
        self._raise_if_error(resp)
        data = resp.json()
        self._token = data["access_token"]
        self._expires_at = time.time() + int(data.get("expires_in", 3000)) - 60
        return self._token

    # ---- shared request + error handling ----
    @staticmethod
    def _raise_if_error(resp):
        if resp.status_code >= 400:
            try:
                body = resp.json()
            except ValueError:
                body = {"message": resp.text}
            raise PayPalError(
                f"HTTP {resp.status_code} {body.get('name', body.get('error', ''))}: "
                f"{body.get('message', body.get('error_description', ''))} "
                f"(debug_id={body.get('debug_id')})"
            )

    def _request(self, method, path, json=None, extra_headers=None):
        headers = {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        resp = requests.request(method, f"{BASE}{path}", headers=headers, json=json, timeout=30)
        self._raise_if_error(resp)
        return resp.json()

    # ---- money in: a member's contribution ----
    def create_order(self, amount, currency="USD", reference=None):
        """Create a sandbox order (a contribution). A buyer must still approve it."""
        unit = {"amount": {"currency_code": currency, "value": f"{amount:.2f}"}}
        if reference:
            unit["reference_id"] = reference
        order = self._request(
            "POST",
            "/v2/checkout/orders",
            json={"intent": "CAPTURE", "purchase_units": [unit]},
            extra_headers={"PayPal-Request-Id": str(uuid.uuid4())},
        )
        approve = next((l["href"] for l in order.get("links", []) if l["rel"] == "approve"), None)
        return {"id": order["id"], "status": order["status"], "approve_url": approve}

    def capture_order(self, order_id):
        """Capture an order after the buyer has approved it."""
        return self._request("POST", f"/v2/checkout/orders/{order_id}/capture")

    # ---- money out: the round's pot ----
    def send_payout(self, receiver_email, amount, note, currency="USD", sender_batch_id=None):
        """Send one payout. sender_batch_id must be unique for 30 days, so a default is generated."""
        batch_id = sender_batch_id or f"tanda-{int(time.time())}-{uuid.uuid4().hex[:6]}"
        body = {
            "sender_batch_header": {
                "sender_batch_id": batch_id,
                "email_subject": "Tanda payout",
                "email_message": "Your savings circle payout",
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {"value": f"{amount:.2f}", "currency": currency},
                    "receiver": receiver_email,
                    "note": note,
                    "sender_item_id": batch_id,
                }
            ],
        }
        data = self._request("POST", "/v1/payments/payouts", json=body)
        header = data["batch_header"]
        return {"payout_batch_id": header["payout_batch_id"], "batch_status": header["batch_status"]}

    def get_payout(self, payout_batch_id):
        """Check a payout's status (it can start as PENDING)."""
        data = self._request("GET", f"/v1/payments/payouts/{payout_batch_id}")
        return {"batch_status": data["batch_header"]["batch_status"], "items": data.get("items", [])}