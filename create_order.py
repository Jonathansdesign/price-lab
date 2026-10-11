from paypal_client import PayPalClient

client = PayPalClient()
order = client.create_order(amount=12.00, reference="test-contribution")
print("Order ID:", order["id"])
print("Status:", order["status"])
print("Buyer approval link:", order["approve_url"])