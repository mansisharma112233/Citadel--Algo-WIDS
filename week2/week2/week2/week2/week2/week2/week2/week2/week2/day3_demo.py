def handle_order_arrival(engine, payload):
    order = payload
    if order.type == "market":
        engine.orderbook.add_market(order.side, order.qty, engine.time)
    else:
        engine.orderbook.add_limit(order)
def submit_order(engine, order, latency):
    arrival_time = engine.time + latency
    event = Event(arrival_time, handle_order_arrival, order)
    engine.schedule_event(event)
def handle_market_close(engine, payload):
    engine.running = False
engine.schedule_event(Event(time=1000, handler=handle_market_close))
from day3_event_engine import MarketEngine, Event
from day2_matching_engine import Order

engine = MarketEngine()

# Submit sell ladder (arrives immediately)
engine.schedule_event(Event(
    1,
    lambda eng, _: eng.orderbook.add_limit(Order("sell", 101, 10, eng.time))
))
engine.schedule_event(Event(
    2,
    lambda eng, _: eng.orderbook.add_limit(Order("sell", 102, 20, eng.time))
))
engine.schedule_event(Event(
    3,
    lambda eng, _: eng.orderbook.add_limit(Order("sell", 103, 30, eng.time))
))

# Market buy with latency
market_buy = Order("buy", float("inf"), 60, 0, "market")
engine.schedule_event(Event(
    10,
    lambda eng, _: eng.orderbook.add_market("buy", 60, eng.time)
))

# Market close
engine.schedule_event(Event(20, lambda eng, _: setattr(eng, "running", False)))

engine.run()

print("Trades:")
for t in engine.orderbook.trades:
    print(t.price, t.qty)

print("Final time:", engine.time)
