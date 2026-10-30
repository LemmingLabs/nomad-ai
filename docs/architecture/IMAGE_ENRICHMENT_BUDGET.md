# Image enrichment budget

Pexels photos are optional suggestions. Each enrichment run allows at most six searches and stops starting searches after eight seconds; each HTTP operation has a two-second connect/read/write/pool timeout. HTTPX timeouts are per network operation, not a strict wall-clock deadline: a request already in progress can finish after the eight-second budget. Quota errors, network errors and malformed responses stop the run. No search queries or credentials are logged. There is no image search cache. Existing attribution is retained; missing images remain absent.

A changed-day refresh removes the old image for every changed day, even when the budget has already been exhausted, so a stale image is not attributed to a new location. Unchanged days retain their images. A full refresh retains existing images if a replacement cannot be found.

## Controlled comparison

For representative days with two distinct search queries each, the table compares the previous loop with the new budget. A mocked provider completes each call in two seconds; a success returns a distinct photo, a miss returns none, and a timeout takes two seconds. These are simulated timings, not production measurements. The former implementation had no explicit timeout and could take longer. The new implementation stops after the first timeout.

| Days | Outcome | Before calls / seconds | After calls / seconds |
| --- | --- | --- | --- |
| 1 | success | 1 / 2 | 1 / 2 |
| 7 or 14 | success | 3 / 6 | 3 / 6 |
| 1 | miss | 2 / 4 | 2 / 4 |
| 7 | miss | 14 / 28 | 4 / 8 |
| 14 | miss | 28 / 56 | 4 / 8 |
| 1 | timeout | 2 / 4 | 1 / 2 |
| 7 | timeout | 14 / 28 | 1 / 2 |
| 14 | timeout | 28 / 56 | 1 / 2 |

The actual number of distinct queries varies with the itinerary. Fast misses may use all six requests before the time budget expires; no live API key is required to exercise the budget tests.
