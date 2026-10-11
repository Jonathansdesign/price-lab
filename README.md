# Tanda

- Saving circles run on trust and spreadsheets, so Tanda estimates each member's reliability, recommends the payout order with the least expected loss, and runs the contributions and payouts through PayPal's sandbox.

Work in Progress


## In Plain English

- In a rotating savings circle, 6 people each put in $100 a month, and one person takes the whole $600 pot each month until everyone has had a turn. Whoever is paid early has effectively borrowed from the others. If they stop paying later, the rest lose money. So the payout order matters. Tanda uses probability to choose it.

## What works currently

- `tanda_stats.py`: simulates members' payment histories and estimates each
  member's chance of paying on time, with a 90% credible interval (Bayes'
  theorem on a grid of values).
- `create_payout.py`: sends a sandbox PayPal payout using the Payouts API.
- `create_order.py`: creates a sandbox PayPal order (a contribution).

## Planned

- Loss model and best payout order (comparing all 720 orders for 6 members)
- AI agent that calls the statistics as a tool and proposes PayPal actions,
  which a human approves
- Simple web app, deployed for judges to try

## Statistics used

- Bernoulli and binomial trials, Bayes' theorem, the law of total probability, CDFs, and hypergeometric probabilities (baseline for a random order).

## Limitations currently

- Member payment histories are simulated. There is no real circle data.
- Everything uses PayPal's sandbox. No real money moves.

## Run it

1. Install Python and run `pip install requests python-dotenv`.
2. Copy `.env.example` to `.env` and fill in your sandbox credentials.
3. `python tanda_stats.py`


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