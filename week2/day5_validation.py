def validate_orderbook(orderbook):
    for _, _, order in orderbook.bids:
        assert order.price >= 0
        assert order.qty >= 0

    for _, _, order in orderbook.asks:
        assert order.price >= 0
        assert order.qty >= 0

    if orderbook.bids and orderbook.asks:
        assert orderbook.bids[0][2].price < orderbook.asks[0][2].price


def validate_tape(df):
    assert (df["price"] >= 0).all()
    assert (df["size"] > 0).all()

