# Citadel–Algo–WIDS  
## Market Microstructure Simulator and Exchange Engine (Python)

This repository contains a step by step implementation of a market microstructure simulator.  
The project is structured week wise and day wise, gradually building from a basic limit order book to a scalable, event driven exchange engine.

The goal of this project is to understand how real financial exchanges work internally, both from a market mechanics perspective and from a software engineering perspective.

The entire implementation is written in Python and is designed to be deterministic, modular, and extendable for future work such as agent based trading and reinforcement learning.

---

## Project Overview

Financial markets are not simple price charts. Behind every trade is an exchange engine that receives orders, prioritizes them, matches buyers and sellers, and records trades in a precise and deterministic manner.

This project builds that engine from scratch.

The work completed so far is divided into two phases:

- **Week 1:** Market microstructure and basic order book mechanics  
- **Week 2:** Engineering the exchange engine using efficient data structures, matching logic, and discrete event simulation  

---

## Week 1 — Market Microstructure and Order Books

### Objective

The objective of Week 1 was to understand how orders become trades inside an exchange and to implement a minimal but correct limit order book.

The focus during this week was correctness and conceptual understanding rather than performance.

---

### Topics Covered

- Limit orders and market orders  
- Bid and ask sides of the order book  
- Price time priority  
- Order matching basics  
- Bid ask spread and liquidity depth  
- Deterministic replay of order streams  

---

### Day 1 — Inside the Exchange

Day 1 focused on understanding how exchanges operate internally.

Topics studied:
- Order types such as market orders, limit orders, IOC, FOK, and post only orders  
- Order queues and time priority  
- Price discovery through order matching  

**Exercise completed:**  
A manual simulation of 15 limit orders and 10 market orders was performed using a spreadsheet to track queue state and matching behavior.

---

### Day 2 — Basic Order Book Implementation

Day 2 focused on converting conceptual understanding into code.

A minimal Python based limit order book was implemented with:
- Separate bid and ask books  
- Basic price time priority  
- Deterministic execution of the same order stream  

This implementation prioritizes clarity and correctness.

---

### Day 3 — Liquidity and Market Depth

This day focused on understanding liquidity rather than adding complex logic.

Concepts studied:
- Bid ask spread  
- Market depth  
- Trade tape  
- Impact of large orders on price  
- Relationship between liquidity and volatility  

Synthetic order flow was used to observe depth and spread behavior.

---

### Week 1 Directory Structure


---

### Key Resources Used (Week 1)

- Barry Johnson, *Algorithmic Trading and DMA*  
- QuantStart: Introduction to Market Microstructure  
- Kyle (1985), Liquidity Model  
- Bouchaud et al., Liquidity in Financial Markets  
- Live order book observation using Binance  

---

## Week 2 — Constructing the Market Engine

### Objective

Week 2 shifts the focus from conceptual correctness to engineering quality.

The goal is to transform the Week 1 order book into a realistic exchange engine that:
- scales to large numbers of orders  
- matches orders correctly under all conditions  
- advances time using discrete events  
- supports deterministic replay and testing  

---

### Day 1 — Advanced Data Structures

Day 1 focused on performance and scalability.

The Week 1 list based order book was refactored to use heap based priority queues.

Key ideas:
- Python lists scale poorly for large order volumes  
- Heaps provide O(log n) insertion and removal  
- Buy orders are implemented as a max heap by inverting prices  
- Sell orders are implemented as a min heap  

A benchmark comparing insertion of 10,000 orders using lists versus heaps demonstrates the performance improvement.

---

### Day 2 — Matching Engine Logic

Day 2 implemented the core matching engine.

This is the heart of the exchange.

Features implemented:
- Price time priority using heap ordering and timestamps  
- Crossing the spread logic  
- Partial fills  
- Walking the order book across multiple price levels  
- Trade object creation with price, quantity, buyer, seller, and timestamp  
- Deterministic validation tests  

A validation test clears the entire ask side using a large market buy order.

---

### Day 3 — Discrete Event Simulation

Day 3 introduced proper time handling.

Financial markets do not use real time delays. They advance time only when events occur.

This day implemented:
- A discrete event scheduler using a priority queue  
- Virtual simulation time  
- Order arrival events  
- Latency modeled as future scheduled events  
- Market close events  
- Deterministic execution order  

The design follows the same conceptual model as SimPy, even though SimPy is not directly used.

---

### Week 2 Directory Structure


---

### Key Resources Used (Week 2)

- Python `heapq` documentation  
- SimPy documentation (conceptual reference)  
- Real Python: Discrete Event Simulation with SimPy  
- Central Limit Order Book reference (Wikipedia)  
- Matching engine design articles  
- Gode and Sunder (1993), Zero Intelligence Traders  
- QuantEcon simulation lectures  

---

## Design Philosophy

- Deterministic and reproducible execution  
- Clear separation between exchange logic and agents  
- Event driven simulation instead of real time delays  
- Python first and research friendly design  
- Ready for extension to agent based models and reinforcement learning  

---

## Future Work

Planned extensions include:
- Order cancellations and modifications  
- Agent based trading strategies  
- Reinforcement learning environments  
- Backtesting execution strategies  
- Transaction cost and slippage modeling  

---

## Summary

By the end of Week 2, this repository contains:
- A functioning limit order book  
- A correct and validated matching engine  
- A discrete event driven exchange simulator  
- A clean and extensible architecture suitable for research and experimentation  
