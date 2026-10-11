import os

from paypal_client import PayPalClient

receiver = os.getenv("PAYPAL_TEST_RECEIVER")
client = PayPalClient()
result = client.send_payout(receiver_email=receiver, amount=5.00, note="Round 1 payout")
print("Payout batch ID:", result["payout_batch_id"])
print("Status:", result["batch_status"])

# Payouts can start as PENDING, so check again:
status = client.get_payout(result["payout_batch_id"])
print("Checked status:", status["batch_status"])