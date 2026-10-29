## Context

The full-trip image cap counts successful photos, while unsuccessful searches can run through multiple queries for every day. Each Pexels request is synchronous. No production latency measurement is available yet.

## Acceptance criteria

- Measure the current provider call count and elapsed time for representative 1-, 7- and 14-day trips with mocked successes, misses and timeouts.
- Define and implement a bounded request/time budget and explicit provider timeouts. Preserve the current API and attribution; leave photos optional rather than inventing a match.
- Handle quota, timeout and unavailable provider without blocking or failing the itinerary indefinitely. Keep changed-day refresh and previously valid images correct.
- Document any cache scope and expiration, and avoid logging credentials or private prompts.

## Verification

Use mocked provider boundaries to check request limits, failures and selective refresh; compare latency/call counts before and after without requiring a live API key.
