## Context

Trip detail returns the first 50 messages in ascending order. The current workspace displays that page without a way to load the rest, so recent messages in longer chats may be missing on reload.

## Acceptance criteria

- Load the most recent messages first while displaying them chronologically; provide an accessible way to load older messages without duplicates or unexpected scroll jumps.
- Define stable ordering for equal timestamps and page boundaries. Keep existing API consumers compatible or document and implement a coordinated contract change.
- Preserve a newly sent message, loading and error/retry behavior, guest handling and chat limits.

## Verification

Test empty, under-50 and over-50 histories, equal timestamps, loading older messages, sending during pagination, reload, and unauthorized access.
