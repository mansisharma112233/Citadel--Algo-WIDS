### Week 2 Day 2 – Matching Engine Logic

The matching engine enforces price-time priority using dual heaps for
bids and asks. Orders are matched whenever the best bid price is greater
than or equal to the best ask price.

Partial fills are handled by decrementing quantities and walking the
book level by level. Market orders ignore price and consume liquidity
until filled or the book is exhausted.

A validation test using a market order that clears the entire ask side
confirms correct matching, trade logging, and book updates.
