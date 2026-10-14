"""Charge the saved PayPal wallet from vault_test.py, with no one clicking approve.

Setup: add this line to your .env (use the Vault ID that vault_test.py printed):
    TEST_VAULT_ID=your_vault_id_here

Run:  python vault_charge_test.py
"""
import os

from paypal_client import PayPalClient, PayPalError

vault_id = os.getenv("TEST_VAULT_ID")
if not vault_id:
    raise SystemExit("Add TEST_VAULT_ID=... to your .env first.")

client = PayPalClient()
try:
    result = client.charge_vaulted(vault_id, amount=5.00, reference="vault-charge-test")
    print("Charge status:", result["status"])
    print("Order ID:", result["id"])
except PayPalError as e:
    print("Charge failed:", e)