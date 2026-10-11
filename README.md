# Tanda

- Saving circles run on trust and spreadsheets, so Tanda estimates each member's reliability, recommends the payout order with the least expected loss, and runs the contributions and payouts through PayPal's sandbox.

Work in Progress

## Setup notes (PayPal sandbox)

1. Sign in to developer.paypal.com with a regular PayPal login.
2. Under Testing Tools > Sandbox Accounts, find the default Business (seller)
   and Personal (buyer) test accounts.
3. Created a payment link/button while logged in as the sandbox Business account.
4. Paid it as the sandbox Personal account in a private browser window.
   (Paying while logged in as the Business account fails: a seller can't pay itself.)
5. Confirmed the payment in both accounts' activity.

## What went wrong and how I fixed it

- **Two different Client IDs:** Pasted the Client ID from the Developer
  Dashboard's Default Application into index.html, but the Buy Button needs the
  Client ID from its own generated snippet (Stacked Buttons tab). They were
  different. Fix: copy the whole <script> line PayPal generates instead of
  assembling it myself. The Default Application's Client ID and Secret are a
  separate pair, which I'll use later for creating orders from code.
- **Which value is the BUTTON_ID:** the snippet's placeholder is
  `BUTTON_ID`, and the dashboard labels it "Hosted ID" (not the same as the
  Client ID). It goes in both places in Part 2 (the container id and
  `hostedButtonId`).
- **Saved the project as a file instead of a folder:** VS Code's Open Folder
  couldn't find index.html inside it. Fix: create a real folder, then create
  index.html inside it.