# Real-Time Card Fraud Detection

A fraud scoring service that helps a card issuer decide, in real time,
whether to approve, block or manually review an online card payment.

## Problem statement

**Context.** Card-not-present (online) fraud is costly for Australian banks
and their customers. This project uses 590,540 online card transactions
from Vesta (IEEE-CIS Fraud Detection dataset), of which about 3.5% are fraud.

**Decision.** For each transaction, the model returns a fraud risk score.
Transactions above a threshold are sent to a fraud analyst for review;
the rest are approved automatically.

**Cost of errors.**
- A missed fraud (false negative) costs the bank the full transaction amount.
- A false alarm (false positive) costs an assumed A$10 of analyst time
  and creates friction for a genuine customer.

The decision threshold is chosen to minimise the total expected cost,
not set at the default of 0.5.

**Success metrics.** Accuracy is misleading here: a model that predicts
"not fraud" for every transaction would be 96.5% accurate but catch nothing.
I therefore use PR-AUC as the main model metric, and total cost (A$)
as the business metric.

**Baseline.** A simple rule-based system (e.g. flag large amounts from new
devices or unusual email domains). The model must clearly beat these rules.

**Constraints.**
- Only information available at the time of the transaction may be used.
- Scoring must be fast enough for payment approval (target: under 100 ms).