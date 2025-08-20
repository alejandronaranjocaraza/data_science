from polygon import RESTClient
from polygon.rest import models


key = "oFqrkL3zTnVJ2GmKVpUiyqjN01GXhj4h"
client = RESTClient(key)

# paginated endpoint. for non-paginated *get is used

aggs = client.get_aggs(
    "AAPL",
    1,
    "day",
    "2025-04-04",
    "2025-04-04",
)

print(aggs)
print(type(aggs))
