# NomadAI Product Feature Audit — 2026-10-29

## Purpose and scope

This review looks for the next useful improvements to the current development product, with a focus on how travelers create, refine, and review trips. It follows the earlier product quality audit and avoids reopening its ten completed issues. It does not treat worldwide planning as shipped and does not propose provider contracts, live booking, or launch-readiness work. Recommendations are proposals, not implemented features.

The review is based on static inspection of the current traveler UI, trip API, persistence model, and backlog. No running-app usability session or analytics review was available. Priorities describe a suggested order and can be adjusted by the team.

## Current product observations

- The itinerary workspace already has day cards, a jump-to-day navigation, route transitions, trip focus mode, estimate/provenance guidance, and explicit degraded-generation notices. The next presentation improvement should make the same itinerary useful outside the interactive workspace.
- The empty chat rotates example prompts as animated text, but those examples are not clickable actions. Once a trip exists, the traveler has only the free-form chat input for requesting changes.
- Signed-in travelers can delete a saved trip from the sidebar. The trip header displays its title, but the current trip API exposes read/list/delete operations and has no title-update route.
- The backend already stores a trip title and has a repository update helper, so renaming an owned trip can fit the existing model without a schema migration.

**Evidence:** [TripPreview.tsx](../../frontend/src/widgets/trip-preview/TripPreview.tsx), [ChatPanel.tsx](../../frontend/src/widgets/chat-panel/ChatPanel.tsx), [SidebarTripItem.tsx](../../frontend/src/widgets/sidebar/SidebarTripItem.tsx), [trips.py](../../backend/app/api/v1/trips.py), [trip_repository.py](../../backend/app/repositories/trip_repository.py), and [TripHeader.tsx](../../frontend/src/widgets/trip-header/TripHeader.tsx).

## Recommended next issues

### QUALITY-11 — Make an itinerary easy to print and keep

**Priority: High · Surface: traveler itinerary**

The trip view is organized for a split-screen chat workspace. There is no print action or print stylesheet, so a traveler cannot produce a clean paper or browser “Save as PDF” copy for offline reference.

**Proposal:** Add a print action and print-specific layout for the itinerary. Keep useful trip context, day headings, activity details, route information, image attribution, estimate/degraded notices, and sponsored labels. Hide interactive chat, navigation, and editing controls. Use the browser print dialog; no PDF service or booking flow is needed.

### QUALITY-12 — Offer contextual one-click trip refinements

**Priority: High · Surface: trip chat**

The empty-state examples teach travelers how to phrase a request, but they are decorative text and disappear once the conversation begins. New users must invent their own first edit request.

**Proposal:** Show a small set of relevant refinement chips, such as reducing long drives, adding a rest day, or making activities easier. Selecting a chip should submit through the existing chat path, so loading state, authentication, usage limits, errors, and itinerary refresh stay consistent. Avoid suggesting changes that the current itinerary cannot support.

### QUALITY-13 — Rename saved trips

**Priority: Medium · Surface: saved trips and trip header**

The sidebar supports deleting a saved trip but offers no way to give it a memorable name. The trip model already stores a title, but the versioned trip API has no update-title endpoint and the traveler UI has no rename action.

**Proposal:** Let the signed-in owner rename a saved trip from its sidebar action menu or trip header. Validate and trim the title, enforce ownership in the API, update the visible list/header after success, and provide clear pending and error states. Keep deletion confirmation behavior intact. Do not add a schema migration.

## Sequencing

1. QUALITY-11 adds immediate utility to the finished itinerary and improves its visual presentation in a common export format.
2. QUALITY-12 makes trip editing more discoverable without introducing a new AI or persistence contract.
3. QUALITY-13 improves saved-trip organization and requires a small end-to-end API capability.

All three belong under the existing `QUALITY-DEV` milestone and `EPIC-PRODUCT-QUALITY` epic. Preserve current guest trip generation/sync, subscriptions and edit limits, sponsored disclosures, and explicit draft/estimate language. No tests were run for this documentation-only review; each implementation issue includes focused verification expectations.

## Review limits

This is a code-based opportunity review, not a visual QA sign-off. Print layout, refinement-chip wording, and rename placement should be checked in the running app on desktop and mobile during implementation. Existing feature availability may change; update this document if the underlying API or interaction changes before these issues are started.
