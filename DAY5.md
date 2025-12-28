## **1\. Introduction and Motivation**

Modern financial markets operate through highly structured electronic exchanges. These exchanges do not decide prices directly. Instead, prices emerge from the interaction of buy and sell orders submitted by many participants. Understanding this internal mechanism is essential before studying trading strategies, market making, or reinforcement learning based agents.

The purpose of this simulator is to recreate the core mechanics of a real exchange in a simplified but realistic manner. Rather than modeling economic value or prediction, the focus is on how orders are processed, how liquidity forms, and how trades are executed. This simulator is designed as a foundational system that can later support more advanced agent behavior and learning based approaches.

Week 1 focuses entirely on building a correct and transparent exchange mechanism. The goal is not complexity, but correctness, clarity, and extensibility.

## **2\. Overview of Real Exchange Behavior**

In real electronic markets, traders interact with the exchange by submitting orders. These orders specify whether the trader wants to buy or sell, how much quantity they want to trade, and sometimes the price at which they are willing to trade. The exchange applies a fixed set of rules to determine which orders trade and at what price.

Most modern equity and cryptocurrency exchanges are order driven. This means all trading activity occurs through a limit order book. There is no direct negotiation between buyers and sellers. Instead, the exchange acts as a neutral matching engine that follows transparent rules.

This simulator mirrors that behavior by implementing a centralized limit order book and a deterministic matching engine.

## **3\. Limit Order Book Structure**

The core component of the simulator is the limit order book. The order book maintains two separate sides:

* The bid side, which contains buy orders  
* The ask side, which contains sell orders

Each order includes a price, quantity, side, and timestamp. Buy orders represent demand, while sell orders represent supply. Together, they define the current market state.

Orders in the book are sorted using price and time priority. Buy orders with higher prices are given preference, and sell orders with lower prices are given preference. When multiple orders exist at the same price, the order that arrived earlier is executed first. This rule reflects how many real exchanges operate, as it is fair, simple, and transparent.

## **4\. Order Types and Execution**

The simulator supports two fundamental order types:

**Limit Orders**  
Limit orders specify a price and quantity. If they cannot be matched immediately, they are added to the order book. These orders provide liquidity to the market and form the depth of the book.

**Market Orders**  
Market orders specify only a quantity and are executed immediately using the best available prices in the book. Market orders consume liquidity and may execute across multiple price levels if the available depth is insufficient at the best price.

When a new order arrives, the exchange checks whether it can be matched against existing orders. A trade occurs when the best buy price is greater than or equal to the best sell price. Trades may be fully or partially executed depending on the quantities involved.

## **5\. Price Formation and Liquidity**

Prices in the simulator are not externally set. Instead, they emerge naturally from order interaction. The best buy price and best sell price define the current bid ask spread. This spread changes dynamically as orders are added, removed, or executed.

Liquidity is represented by the number of limit orders available at different price levels. When many orders are clustered near the current price, the market appears liquid and spreads tend to be small. When the book is thin, even small market orders can cause noticeable price movement.

This behavior reflects real market dynamics, where liquidity, depth, and price impact are closely related. Importantly, liquidity is not a parameter in the simulator but an emergent property of order flow.

## **6\. Deterministic and Event Based Simulation**

The simulator uses a discrete event model rather than real time processing. Orders are processed sequentially based on timestamps. This ensures that the outcome of the simulation depends only on the order stream and not on system timing or randomness.

A key design choice is deterministic replay. When the same sequence of orders is processed multiple times, the simulator produces identical trades in the same order. This property is essential for debugging, analysis, and comparison of experiments.

Determinism is also critical for future reinforcement learning experiments, where reproducibility is required to evaluate agent performance reliably.

## **7\. Agent and Environment Separation**

In the simulator design, agents are conceptually separated from the exchange. Agents do not modify the order book directly. Instead, they interact with the market only by submitting orders.

The market environment processes these orders, updates the order book, and generates trades. Agents may observe market outputs such as best bid, best ask, depth, or recent trades, but they do not have access to the internal data structures of the exchange.

This separation mirrors real trading systems and ensures that the exchange remains neutral and rule based.

## **8\. System Architecture and Modularity**

The simulator is designed with modular components:

* Agents generate orders  
* The market environment receives and processes orders  
* The order book stores and matches orders  
* A trade logger records executions

Each component has a clear responsibility. This modular design makes the system easier to understand, test, and extend. It also ensures that future features can be added without rewriting core logic.

For example, adding new agent types, stochastic order arrivals, or cancellation logic can be done independently of the matching engine.

## **9\. Relevance to Market Microstructure Research**

Market microstructure research emphasizes the importance of trading rules and order flow in shaping market outcomes. Even simple agents interacting through a realistic exchange can produce meaningful market behavior.

This simulator aligns with that perspective by focusing on exchange mechanics rather than strategic complexity. It provides a controlled environment where the impact of order flow, liquidity, and matching rules can be studied in isolation.

## **10\. Future Extensions**

While the current simulator is minimal, it is designed to support future extensions. Possible next steps include:

* Order cancellations and modifications  
* Stochastic order arrival processes  
* Market making agents  
* Reinforcement learning agents with defined observation and action spaces  
* Performance metrics such as execution cost and inventory risk

Because the core exchange logic is clean and deterministic, these extensions can be added incrementally without compromising correctness.

## **11\. Conclusion**

This simulator successfully captures the essential mechanics of a real electronic exchange. By focusing on order driven trading, price time priority, deterministic execution, and modular design, it provides a strong foundation for studying market behavior.

The system is intentionally simple at this stage, but its structure allows it to grow into a powerful experimental platform for agent based modeling and learning driven market analysis in later stages of the project.

