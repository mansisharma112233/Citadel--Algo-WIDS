from dataclasses import dataclass, field
import time
from typing import Optional


@dataclass
class Order:
    order_id: int
    side: str  # "BUY" or "SELL"
    price: Optional[float]
    quantity: int
    timestamp: float = field(default_factory=time.time)
    status: str = "OPEN"

    def __post_init__(self) -> None:
        assert self.side in ("BUY", "SELL"), "side must be 'BUY' or 'SELL'"
        assert self.quantity > 0, "quantity must be > 0"
        if self.price is not None:
            assert self.price > 0, "price must be > 0"
"""
Order data class for limit order book.
"""
from dataclasses import dataclass, field
import time


@dataclass
class Order:
    """
    Represents a limit order in the order book.
    
    Attributes:
        order_id: Unique identifier for the order
        side: Order side, either "BUY" or "SELL"
        price: Limit price (None for market orders)
        quantity: Number of shares/units
        timestamp: Order creation time (auto-filled if None)
        status: Order status (default "OPEN")
    """
    order_id: int
    side: str
    price: float | None
    quantity: int
    timestamp: float = field(default=None)
    status: str = "OPEN"
    
    def __post_init__(self):
        """Validate order parameters."""
        # Validate side
        assert self.side in ("BUY", "SELL"), f"Invalid side: {self.side}. Must be 'BUY' or 'SELL'"
        
        # Validate quantity
        assert self.quantity > 0, f"Invalid quantity: {self.quantity}. Must be > 0"
        
        # Validate price if provided
        if self.price is not None:
            assert self.price > 0, f"Invalid price: {self.price}. Must be > 0"
        
        # Auto-fill timestamp if not provided
        if self.timestamp is None:
            self.timestamp = time.time()
