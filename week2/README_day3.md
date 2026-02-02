# Week 2 — Day 3: Discrete Event Simulation (Event Loop)

## Summary

### Continuous vs Discrete Time
Continuous-time simulations track state changes in real time. Discrete-event simulations jump directly from one event to the next, skipping idle periods. This is far more efficient for modeling systems where events occur at specific moments (e.g., order arrivals, trades).

### Why sleep() is Wrong
Using `time.sleep()` ties simulation speed to wall-clock time. A 1-hour simulation would take 1 hour to run. Discrete-event simulation decouples simulation time from real time, allowing millions of events to be processed in seconds.

### Heap as Scheduler
Events are stored in a min-heap keyed by `(timestamp, sequence_id)`. The heap ensures O(log n) insertion and O(log n) extraction of the next event. This is efficient even with thousands of pending events.

### Deterministic Event Ordering
Events are ordered first by timestamp, then by sequence_id (insertion order). This guarantees reproducible results: events scheduled at the same timestamp execute in the order they were added.

## Validation Test
A test function `test_event_ordering()` is included in `event_loop.py`. It verifies that events are processed in correct timestamp order.

Run via:
```
python -c "from week2.engine.event_loop import test_event_ordering; test_event_ordering()"
```

This completes Week 2 Day 3.
