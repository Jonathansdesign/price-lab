# Tanda

Savings circles run on trust and spreadsheets, so Tanda estimates each member's
reliability, recommends the payout order with the least expected loss, and moves
contributions and payouts through PayPal's sandbox. (Work in progress. An AI agent
to coordinate the steps is planned and not built yet.)

Built for the PayPal AI Hackathon (Oct 2026). Everything uses PayPal's **sandbox**:
no real money moves, and all member payment histories used for the statistics are
**simulated**.

## The idea in plain English

In a rotating savings circle (a tanda, susu, or hui), 6 people each put in $100 a
month, and one person takes the whole $600 pot each month until everyone has had a
turn. Whoever is paid early has effectively borrowed from the others. If they stop
paying afterward, the rest lose money. So the payout order matters, and Tanda uses
probability to choose it.

## Status

| Piece | File(s) | Status |
|---|---|---|
| Estimate each member's on-time probability (Bayes) | `tanda_stats.py` | Built, runs on simulated data |
| Score all payout orders, pick the least risky | `tanda_loss.py` | Built, runs on simulated data |
| PayPal client (token reuse, errors, orders, payouts, vault) | `paypal_client.py` | Built, tested against the sandbox |
| Create a sandbox order | `create_order.py` | Works |
| Send a sandbox payout | `create_payout.py` | Works (payout arrives in the buyer account) |
| Save a member's PayPal wallet (approve once) | `vault_test.py` | Works for one sandbox account |
| Charge a saved wallet with no one present | `vault_charge_test.py` | Works for one sandbox account |
| Round runner (one full round, end to end) | | Not built |
| AI agent (calls the statistics and PayPal as tools, human approves) | | Not built, LLM not chosen yet |
| Web app and hosted demo (Render) | | Not built |
| Simulation study (validation of the model) | | Not built |

## How it works

1. **Estimate** (`tanda_stats.py`). Each member has a hidden probability of paying
   on time. From their payment history (1 = on time, 0 = late or missed), Bayes'
   theorem updates a belief over a grid of candidate values (5% to 95%). Output: a
   predicted on-time probability and a 90% credible interval.
2. **Score orders** (`tanda_loss.py`). For every possible payout order (720 for 6
   members), compute the distribution of total missed payments, then the expected
   dollar loss and the chance of a bad outcome (3 or more missed payments).
3. **Move money** (`paypal_client.py`). Contributions are charged to each member's
   saved PayPal wallet, and the round's pot is sent to the winner with the Payouts
   API. A refused charge raises an error that becomes a 0 in that member's history.

### Model assumptions

- N members each pay C per round. The member in slot s receives the pot in round s.
- A member who has **not yet** received the pot keeps paying. The risk is a member
  who already took the pot and then misses payments (they still owe N - s).
- Given a member's true on-time probability, missed payments are binomial. Members
  are independent. A late payment counts as a missed one.
- Without the second assumption every order would have the same total loss, and
  there would be nothing to optimize.

### Statistics used

Bernoulli and binomial trials, Bayes' theorem, the law of total probability, PMFs
and CDFs (tail probability), convolution of PMFs, and exhaustive search over all
N! orders.

## Results so far (one simulated circle, seed 42)

Six simulated members, 8 months of history each. Model-estimated numbers:

| Order | Expected loss | Chance of 3+ missed payments |
|---|---|---|
| Best: Ana, Ben, Femi, Carla, Dev, Elena | $283 | 54.7% |
| Random order (average over all 720) | $438 | 82.6% |
| Worst | $593 | 95.7% |

This is a single run, scored with the model's own beliefs. A multi-run validation
against the true probabilities is planned (see Roadmap).

## What went wrong along the way

- **Two different Client IDs.** The Buy Button's generated snippet has its own
  Client ID, separate from the Default Application's Client ID and Secret. The
  Python code uses the Default Application pair.
- **Sandbox vs. real accounts.** The "Business account" in the guides is a free
  sandbox test account that PayPal creates automatically, not a real one.
- **A seller can't pay itself.** Paying a test button while logged in as the
  sandbox Business account fails. Use a private window and a sandbox Personal account.
- **Payouts start as PENDING.** The client checks the status again afterward.
- **Vault orders label their link differently.** A normal order's approval link is
  `approve`, but a vault order's is `payer-action`, so the client handles both.
- **Fees.** The sandbox simulated a $0.66 fee on a $5.00 charge, so money collected
  in a round is slightly less than the sum of contributions.

## Limitations (honest)

- **Simulated data.** There is no real circle data. Histories are generated from
  known probabilities, so results show how the method behaves, not how real people behave.
- **Sandbox only.** Pooling and paying out real money is regulated, and saving
  payment methods for live use likely needs extra PayPal approval. Neither is covered here.
- **Small samples mislead.** With 8 months of history, a 45% payer who got lucky
  looks reliable (the model ranked "Femi" third). The 90% intervals show this uncertainty.
- **The order search confirmed a simple rule.** Across 200 simulated circles, the
  best order always matched "most reliable first." The added value is the risk
  numbers, not a surprising order.
- **One real member so far.** Only one sandbox Personal account has a saved wallet.
  The other members are simulated until more accounts are set up.

## Run it

1. Install Python, then run `pip install requests python-dotenv`.
2. Copy `.env.example` to `.env` and fill in your sandbox credentials
   (Developer Dashboard, Apps & Credentials, Sandbox tab, Default Application):
   ```
   PAYPAL_CLIENT_ID=
   PAYPAL_CLIENT_SECRET=
   PAYPAL_TEST_RECEIVER=   # a sandbox Personal account email
   TEST_VAULT_ID=          # printed by vault_test.py
   ```
3. Statistics (no PayPal needed): `python tanda_stats.py` and `python tanda_loss.py`
4. PayPal sandbox: `python create_order.py`, `python create_payout.py`,
   `python vault_test.py` (approve in a private window as a sandbox Personal
   account), then `python vault_charge_test.py`.

Never commit `.env`. It is listed in `.gitignore`.

## Roadmap

- Round runner: charge saved wallets, record successes and failures, update
      the statistics, rescore the order, pay out the pot
- Simulation study: loss versus random and best-possible orders over many
      circles, plus interval coverage
- Simple web app
- AI agent: calls the statistics and PayPal client as tools, with human
      approval before money moves
- Deploy a hosted demo on Render
- Demo video and final write-up

## Notes

- Built with assistance from an AI for coding snippets and explanations. I reviewed the code and can explain it.
- Created after the hackathon began (Oct 10, 2026). The early Buy Button test was
  setup practice, not part of the project.

