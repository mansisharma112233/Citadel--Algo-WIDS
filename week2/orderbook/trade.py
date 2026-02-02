from dataclasses import dataclass


@dataclass
class Trade:
    trade_id: int
    price: float
    quantity: int
    buyer_order_id: int
    seller_order_id: int
    timestamp: float

    def __post_init__(self) -> None:
        assert self.price > 0, "price must be > 0"
        assert self.quantity > 0, "quantity must be > 0"
