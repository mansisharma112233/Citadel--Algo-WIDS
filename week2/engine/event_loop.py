"""
Discrete Event Simulation Engine.

This module provides event loop implementations for the market simulator.

WHY HEAPQ:
    A min-heap allows O(log n) insertion and O(log n) extraction of the
    earliest event. This is efficient even with thousands of pending events,
    compared to O(n) for sorted list insertion.

WHY SEQUENCE_ID:
    When two events have the same timestamp, we need a deterministic tie-breaker.
    The sequence_id ensures events scheduled at the same time are processed in
    the order they were scheduled (FIFO), guaranteeing reproducible simulations.

WHY TIME IS ADVANCED ONLY VIA EVENTS:
    In discrete-event simulation, nothing happens between events. Time "jumps"
    directly from one event to the next. This is far more efficient than
    continuous simulation (no idle loops) and ensures determinism (no dependency
    on wall-clock time or sleep()).
"""

import heapq
import itertools
from typing import Callable, Any, Optional
from week2.engine.event import Event


class EventLoop:
    """Basic event loop using Event dataclass."""

    def __init__(self):
        self.current_time = 0.0
        self.event_queue: list[Event] = []
        self._seq = itertools.count(1)

    def schedule_event(self, timestamp: float, event_type: str, payload: dict) -> None:
        event = Event(
            timestamp=timestamp,
            sequence_id=next(self._seq),
            event_type=event_type,
            payload=payload,
        )
        heapq.heappush(self.event_queue, event)

    def run(self, handler) -> None:
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.timestamp
            handler(event)


class MarketEventLoop:
    """
    Core event loop for market simulation.

    Connects agents, matching engine, and analytics via scheduled events.
    Uses a heap-based priority queue for O(log n) event scheduling.

    Events are tuples: (timestamp, sequence_id, event_function, args)
    - timestamp: simulation time when event fires
    - sequence_id: tie-breaker for deterministic ordering
    - event_function: callable to execute
    - args: arguments to pass to the function
    """

    def __init__(self, matching_engine=None):
        self.current_time: float = 0.0
        self.event_queue: list[tuple] = []  # heapq of (timestamp, seq_id, func, args)
        self._sequence_id: int = 0
        self.matching_engine = matching_engine
        self._tape = None  # TradeTape instance
        self._snapshots = None  # L1Snapshots instance
        self.snapshot_callback: Optional[Callable] = None  # Placeholder for snapshot recording
        self._running: bool = False

    def set_tape(self, tape) -> None:
        """Connect a TradeTape instance for trade recording."""
        self._tape = tape

    def set_snapshots(self, snapshots) -> None:
        """Connect an L1Snapshots instance for snapshot recording."""
        self._snapshots = snapshots
        # Also set as callback for backward compatibility
        if snapshots is not None:
            self.snapshot_callback = snapshots.record

    # Property aliases for backward compatibility
    @property
    def tape(self):
        return self._tape

    @tape.setter
    def tape(self, value):
        self._tape = value

    def schedule_event(self, timestamp: float, event_function: Callable, *args: Any) -> None:
        """
        Schedule an event to fire at the given timestamp.

        Events with the same timestamp are ordered by sequence_id (FIFO).
        """
        self._sequence_id += 1
        event = (timestamp, self._sequence_id, event_function, args)
        heapq.heappush(self.event_queue, event)

    def run(self) -> None:
        """
        Run the event loop until all events are processed or market closes.

        Time advances discretely from event to event—no idle waiting.
        """
        self._running = True
        while self.event_queue and self._running:
            timestamp, seq_id, event_function, args = heapq.heappop(self.event_queue)
            self.current_time = timestamp
            event_function(*args)

    def process_order(self, order) -> list:
        """
        Process an order through the matching engine.

        Returns list of trades generated.
        If tape is connected, trades are recorded automatically.
        """
        if self.matching_engine is None:
            return []

        trades_before = len(self.matching_engine.trades)
        self.matching_engine.process_order(order)
        new_trades = self.matching_engine.trades[trades_before:]

        # Record trades to tape if connected
        if self._tape is not None:
            self._tape.record_trades(new_trades, self.current_time)

        return new_trades

    def snapshot_event(self) -> None:
        """
        Record a snapshot of current book state.

        If snapshots object is set, calls record() with current orderbook.
        If snapshot_callback is set, calls it with current orderbook.
        Automatically reschedules next snapshot at current_time + 1 second.
        """
        if self._snapshots is not None and self.matching_engine is not None:
            self._snapshots.record(self.current_time, self.matching_engine.orderbook)
        elif self.snapshot_callback is not None and self.matching_engine is not None:
            self.snapshot_callback(self.current_time, self.matching_engine.orderbook)

        # Reschedule next snapshot in 1 second (if still running)
        if self._running:
            self.schedule_event(self.current_time + 1.0, self.snapshot_event)

    def start_snapshots(self, start_time: float) -> None:
        """
        Begin periodic snapshot recording.

        Schedules first snapshot at start_time, then every 1 second thereafter.
        """
        self.schedule_event(start_time, self.snapshot_event)

    def market_close(self) -> None:
        """
        Close the market and stop the event loop.

        Clears all remaining scheduled events.
        """
        self._running = False
        self.event_queue.clear()


def test_event_ordering():
    loop = EventLoop()
    order = []

    def handler(event):
        order.append((event.timestamp, event.event_type))

    loop.schedule_event(5, "A", {})
    loop.schedule_event(1, "B", {})
    loop.schedule_event(3, "C", {})

    loop.run(handler)

    assert order == [(1, "B"), (3, "C"), (5, "A")]


def test_market_event_loop():
    """Test MarketEventLoop basic functionality."""
    loop = MarketEventLoop()
    execution_order = []

    def event_a():
        execution_order.append(("A", loop.current_time))

    def event_b():
        execution_order.append(("B", loop.current_time))

    def event_c():
        execution_order.append(("C", loop.current_time))

    loop.schedule_event(5.0, event_a)
    loop.schedule_event(1.0, event_b)
    loop.schedule_event(3.0, event_c)

    loop.run()

    assert execution_order == [("B", 1.0), ("C", 3.0), ("A", 5.0)]
