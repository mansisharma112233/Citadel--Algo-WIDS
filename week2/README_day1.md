Week 2 — Day 1: Advanced Data Structures for a Limit Order Book

Summary
- List-based order books keep orders in a simple Python list. Inserting an order at the correct sorted position requires shifting elements, which is O(n) per insertion — inefficient for large books.
- Heap-based books maintain best-price access in O(log n) time (heap push/pop), and when combined with per-price FIFO queues they support efficient best-price discovery while preserving FIFO within price levels.
- FIFO at each price level is important because orders at the same price must be executed in arrival order to be fair.
- A simple benchmark comparing 10,000 BUY limit order insertions (list vs heap-based) was included in week2/benchmarks/benchmark_insertion.py.

This completes Week 2 Day 1 (no matching, cancellations, or analytics implemented).
