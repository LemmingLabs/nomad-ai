# Chat history pagination

Existing `GET /trips/{id}` and `GET /trips/{id}/messages?limit=50&offset=0` consumers retain their chronological, oldest-first offset pages. Equal timestamps are ordered by message ID. The traveler workspace opts in to `GET /trips/{id}?recent_messages=true` for the latest 50 messages, still returned chronologically. Its `messages.has_more` indicates whether earlier messages exist.

To load older messages, request `GET /trips/{id}/messages?recent=true&before_id={oldest_message_id}`. The cursor is exclusive and scoped to the same authorized trip; an unknown or foreign cursor returns 400 after ownership checks. Results use `(created_at, id)` ordering and are returned chronologically, with `has_more` indicating whether another earlier page exists. Offset and cursor pagination cannot be combined. Messages added after a page was loaded do not move its cursor boundary.

The client prepends and deduplicates older pages without discarding in-flight messages, retains the scroll position on a prepend, and offers a retry when an older page fails. Guest chat remains disabled. History is loaded only for authenticated users with access to the trip.
