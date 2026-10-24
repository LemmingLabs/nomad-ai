## Outcome

Travelers can explicitly choose a supported country and destination, then generate, save, reopen, and edit a trip with that context. Kyrgyzstan remains the compatibility baseline and existing trips keep their original itinerary.

## Why this phase comes first

The current generation flow is Kyrgyzstan-specific. Country expansion cannot be completed safely by changing only the prompt or adding a frontend dropdown: the request contract, persistence, chat context, enrichment consumers, and guest transfer must agree on the selected destination.

## Completion means

- Country and destination have stable identifiers and an explicit supported/unsupported state.
- Generation request, response, saved trip, chat edit, and guest sync carry the selected destination consistently.
- Existing trips and clients continue to behave as Kyrgyzstan trips during the transition.
- The traveler UI only offers destinations the system is prepared to serve.

## Risks and guardrails

- Do not infer a country from a free-text prompt as the source of truth.
- Do not claim global availability because an LLM accepts a country name.
- Schema changes require an Alembic migration; do not rewrite applied migrations.
- Keep responses backward compatible while old clients may still omit destination fields.
