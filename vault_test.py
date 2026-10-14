"""One-time test: can this sandbox app save a member's PayPal so later rounds
can be charged without them clicking approve again?

Run:  python vault_test.py
"""
from paypal_client import PayPalClient, extract_vault

client = PayPalClient()

order = client.create_order(amount=5.00, reference="vault-test", save_payment_method=True)
print("Order ID:", order["id"])
print("Status:", order["status"])
print("\nOpen this link, log in as a sandbox PERSONAL account, and approve:")
print(order["approve_url"])

input("\nAfter you approve (the page may redirect to example.com, that's fine), press Enter here...")

result = client.capture_order(order["id"])
print("\nCapture status:", result.get("status"))

vault = extract_vault(result)
print("Vault status:", vault["status"])
print("Vault ID:", vault["vault_id"])
print("Customer ID:", vault["customer_id"])

if vault["vault_id"]:
    print("\nSUCCESS: the payment method was saved. Keep the Vault ID and Customer ID for this member.")
elif vault["status"] == "APPROVED":
    print("\nPayPal is still saving it. Wait a few seconds and run: python -c \"from paypal_client import PayPalClient; import json; print(json.dumps(PayPalClient().get_order('" + order["id"] + "'), indent=2))\"")
else:
    print("\nNo vault information came back. Paste the Capture status and Vault lines (not your Secret).")