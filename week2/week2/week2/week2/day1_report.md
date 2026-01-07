### Week 2 Day 1 – Advanced Data Structures

The Week 1 order book was functionally correct but relied on list-based
operations, which scale poorly for large numbers of orders.

In Week 2 Day 1, the order book was refactored to use a dual-heap
architecture. Buy orders are stored in a max-heap by inverting prices,
and sell orders are stored in a min-heap.

A timing experiment comparing list insertion and heap insertion for
10,000 orders showed that heap-based insertion is significantly faster,
with O(log n) complexity compared to O(n) for lists.

This refactor makes the exchange engine scalable and suitable for
backtesting and high-frequency order flow.
