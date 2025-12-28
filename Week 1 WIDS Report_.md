Week 1 WIDS Report:  
Report:  
Market Microstructure Simulator: Market Mechanics and Design Choices

### **1\. Introduction**

The purpose of this project is to understand how real financial exchanges function internally. Instead of focusing on trading strategies, predictions, or profit making, the goal is to study the basic mechanisms that convert incoming buy and sell orders into executed trades. Modern electronic markets such as stock exchanges and cryptocurrency exchanges rely on a limit order book, and this simulator aims to recreate that structure in a clear and simplified form.

Week 1 focuses on building the foundation of the simulator. At this stage, the emphasis is on correctness, clarity, and structure rather than complexity. By the end of the week, the simulator should accurately represent how orders arrive, how they are stored, how they are matched, and how prices emerge from this process.

### **2\. Market Structure and Order Flow**

The simulated market is an order driven market. All trading activity occurs through a centralized limit order book. Traders interact with the market by submitting orders, which are processed sequentially by the exchange. There is no direct negotiation between buyers and sellers.

Two main order types are supported. Limit orders specify a price and quantity and are added to the order book if they are not immediately matched. These orders provide liquidity to the market. Market orders specify only a quantity and are executed immediately using the best available prices in the order book. These orders consume liquidity.

The exchange maintains two separate collections of orders. The bid side contains buy orders, and the ask side contains sell orders. Together, these collections represent the current state of supply and demand in the market. Prices are not set externally but arise naturally from this interaction.

### **3\. Limit Order Book Mechanics**

The order book maintains two sides. The bid side stores buy orders sorted by highest price first. The ask side stores sell orders sorted by lowest price first. Within each price level, orders are executed in the order they arrive.

When a new order arrives, the exchange checks whether it can be matched against existing orders. If a crossing condition exists, trades are executed immediately. Otherwise, the order is added to the book. Partial executions are supported, allowing realistic handling of different order sizes.

### **4\. Liquidity and Emergent Market Properties**

Liquidity is not explicitly programmed into the simulator. Instead, it emerges from the distribution of limit orders in the book. When many orders are placed near the current price, spreads become narrow and the market appears liquid. When few orders are present, spreads widen and price impact increases.

Even when agents behave randomly, the exchange mechanism itself produces structured outcomes such as stable spreads and non trivial depth profiles. This observation aligns with classical results showing that realistic exchange rules alone can generate meaningful market behavior.

### **5\. Determinism and Reproducibility**

The simulator is designed to behave deterministically. All randomness is external and comes from the order stream. The exchange processes orders sequentially using timestamps, ensuring reproducible outcomes.

This design choice is particularly important for research and learning based applications. Deterministic environments allow experiments to be repeated and compared reliably, which is essential for evaluation and debugging.

### **6\. Agent and Environment Interaction**

Agents interact with the market only by submitting orders. They do not have direct access to the internal state of the order book. The market environment processes orders and produces trades, which can then be observed by agents.

### **7\. Extensibility and Future Work**

The simulator is intentionally minimal at this stage. However, its structure allows for easy extension. Features such as order cancellations, stochastic arrival processes, more sophisticated agents, and reinforcement learning environments can be added without rewriting the matching engine.

This staged approach ensures that correctness is maintained as complexity increases.

### **8\. Conclusion**

By focusing on order flow, matching rules, and deterministic execution, the simulator captures the essential behavior of real financial exchanges. It provides a clean and extensible platform for studying market dynamics and for building more advanced agent based and learning driven models in later stages of the project.

