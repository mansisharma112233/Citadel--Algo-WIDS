import time
import random
import heapq
from engine import Order

N = 10_000

# -------- List-based insertion --------
orders_list = []
start = time.time()

for i in range(N):
    price = random.randint(90, 110)
    orders_list.append((price, i))
    orders_list.sort()

list_time = time.time() - start

# -------- Heap-based insertion --------
heap = []
start = time.time()

for i in range(N):
    price = random.randint(90, 110)
    heapq.heappush(heap, (price, i))

heap_time = time.time() - start

print(f"List insertion time: {list_time:.4f} seconds")
print(f"Heap insertion time: {heap_time:.4f} seconds")
