## Context

Trip generation and enrichment failures are explicitly marked as degraded, but several exception paths in the trip service use `print` while other paths use the configured logger.

## Goal

Make generation failures easier to diagnose consistently while preserving clear degraded behavior and avoiding personal trip content in logs.

## Acceptance criteria

- AI generation, place enrichment, routing, and image enrichment failures use the application logger instead of `print`.
- Log events include a stable stage/event name and useful non-sensitive context.
- User prompts, credentials, and unnecessary personal trip details are not logged.
- Existing failure reasons and traveler-facing degraded state remain intact.
- Log level and traceback behavior are appropriate for expected provider outages versus unexpected failures.

## Verification

Exercise representative failed and successful generation/enrichment paths and confirm logs are structured and the traveler still sees accurate degraded states.
