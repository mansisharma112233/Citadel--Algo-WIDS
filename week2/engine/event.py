from dataclasses import dataclass


@dataclass(order=True)
class Event:
    timestamp: float
    sequence_id: int
    event_type: str
    payload: dict
