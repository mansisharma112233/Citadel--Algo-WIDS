Day 3 introduced a discrete event simulation framework using a heap-based
scheduler. Time advances only when events occur, ensuring determinism and
reproducibility. Latency is modeled by scheduling future order arrival
events rather than using sleep. This event-driven design mirrors SimPy’s
environment-process-event model and is suitable for realistic market
simulation.
