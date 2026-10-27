# NomadAI Product Quality Audit — 2026-10-27

## Purpose and scope

This is a code and interface review to guide the next round of product improvements. It focuses on the existing development product: trip creation, guest trips and chat, itinerary review, and the business/admin shell. It does not propose launch readiness, provider contracts, or live booking work. No product code was changed as part of this review.

The findings below are based on static source inspection and the checked-in UI screenshots in `docs/assets/screenshots/`. Screenshots may not reflect the current build; visual suggestions should be checked against the running app before implementation. No runtime usability session or analytics review was available. The priorities are proposed sequencing, not commitments.

## Highest-value findings

### AUDIT-01 — Make supported destinations clear from the first screen

**Priority: High · Surface: traveler home and trip creation**

The home page says “Plan your next adventure” and “Tell the AI where you want to go,” while the form later limits selection to destinations currently supported by NomadAI. The opening screen can set a broader expectation than the actual destination selector supports.

**Evidence:** [HomePage.tsx](../../frontend/src/pages/home/HomePage.tsx#L79) and [GenerateTripForm.tsx](../../frontend/src/widgets/generate-trip-form/GenerateTripForm.tsx#L145).

**Suggested improvement:** Name the destinations available in the current build on the home screen, or show a small “Currently available” destination preview beside the create-trip action. Keep that list driven by the destinations API so the text does not go stale as coverage changes.

### AUDIT-02 — Remove the duplicate sign-in prompt on guest trips

**Priority: High · Surface: guest trip chat**

An unauthenticated traveler sees a sign-in explanation inside `ChatPanel` and a second sign-in prompt directly below it. The repeated call to action takes space from the conversation and makes it less clear whether the two prompts lead to different outcomes.

**Evidence:** [TripPage.tsx](../../frontend/src/pages/trip/TripPage.tsx#L195) and [TripPage.tsx](../../frontend/src/pages/trip/TripPage.tsx#L215).

**Suggested improvement:** Keep one concise prompt with a single sign-in action. State plainly that signing in syncs the guest trip, and preserve the guest’s itinerary while authentication completes.

### AUDIT-03 — Expose selected form options and stepper controls accessibly

**Priority: High · Surface: trip creation form**

Budget, interests, and travel style are selectable buttons whose selected state is only represented with `data-active`; the controls do not expose a selected state such as `aria-pressed` or radio semantics. The day stepper uses icon-only minus and plus buttons without accessible names. A screen-reader user may not learn which options are selected or what the stepper buttons do.

**Evidence:** [GenerateTripForm.tsx](../../frontend/src/widgets/generate-trip-form/GenerateTripForm.tsx#L198), [GenerateTripForm.tsx](../../frontend/src/widgets/generate-trip-form/GenerateTripForm.tsx#L220), [GenerateTripForm.tsx](../../frontend/src/widgets/generate-trip-form/GenerateTripForm.tsx#L251), and [GenerateTripForm.tsx](../../frontend/src/widgets/generate-trip-form/GenerateTripForm.tsx#L322).

**Suggested improvement:** Use radio-group semantics for single-choice budget and travel style, toggle-button semantics for interests, and explicit labels such as “Decrease trip length” and “Increase trip length.” Check visible keyboard focus and selected-state contrast at the same time.

### AUDIT-04 — Explain what the budget range means

**Priority: Medium · Surface: trip creation form and itinerary summary**

Budget choices show dollar ranges (`$200-500`, `$500-1200`, `$1200+`) but do not say whether those figures are USD, per traveler, or for the whole trip. The form also allows destination selection, so a currency assumption may become confusing as destination coverage grows.

**Evidence:** [GenerateTripForm.tsx](../../frontend/src/widgets/generate-trip-form/GenerateTripForm.tsx#L15).

**Suggested improvement:** Clarify currency, time span, and whether the range is per traveler or group total. If budgets are qualitative rather than enforced cost estimates, say that directly and repeat the meaning in the generated trip summary.

### AUDIT-05 — Bring the business/admin navigation into a responsive layout

**Priority: Medium · Surface: business and admin panel**

The shared dashboard shell always renders a 16-rem sidebar beside the content and provides no small-screen navigation treatment. On narrow screens this can leave little room for tables, forms, and moderation details.

**Evidence:** [DashboardShell.tsx](../../businessPanel/src/app/layouts/DashboardShell.tsx#L25).

**Suggested improvement:** Add a compact navigation pattern for small viewports, then check the sponsored-place form, moderation table, and dashboard cards at phone and tablet widths. Keep the current desktop navigation as the wide-screen layout.

### AUDIT-06 — Replace provider `print` calls with consistent structured logs

**Priority: Medium · Surface: generation and enrichment diagnostics**

The trip service correctly marks failed AI generation as a degraded mock draft and adds reasons when enrichment fails. Several exception paths still use `print`, while other nearby paths use the module logger. This makes local diagnosis and future log filtering less consistent.

**Evidence:** [trip_service.py](../../backend/app/services/trip_service.py#L727), [trip_service.py](../../backend/app/services/trip_service.py#L770), [trip_service.py](../../backend/app/services/trip_service.py#L793), and [trip_service.py](../../backend/app/services/trip_service.py#L807).

**Suggested improvement:** Use structured logger calls with stable event names and the failure stage, while keeping the existing degraded status visible to the traveler. Avoid putting user prompts or other personal trip content into logs.

## Additional product opportunities

These are design directions to explore after the highest-value fixes, not confirmed defects.

1. **Make the first trip-creation step feel shorter.** The form is a stack of separate sections for destination, budget, trip length, interests, style, and a free-form brief. Consider grouping the required choices into a compact first step and keeping optional preferences behind an expandable “More preferences” section. Preserve a clear review of submitted values.
2. **Make itinerary actions easier to scan.** On the trip screen, test whether day headings, travel time, estimated durations, and practical notes can be distinguished at a glance. Keep AI suggestions, verified catalog details, route estimates, and sponsored places visibly distinct.
3. **Use one visual language across traveler and business apps.** The traveler app uses shared SCSS design tokens, while the business shell has separately declared Tailwind utility styling. Review typography, spacing, focus rings, buttons, and empty states side by side; align the most visible shared patterns where that improves consistency.
4. **Tighten the home screen’s empty state.** The current welcome screen has a single message and create action. A supported-destination preview and one short example of the resulting itinerary could help a first-time guest understand what they can do before opening the long form.
5. **Keep development fallback content destination-aware.** The development mock itinerary currently names Kyrgyzstan locations directly. Before enabling another destination in generation, pass destination context into the mock path or clearly identify the mock as Kyrgyzstan-only so a failed provider cannot produce a draft for the wrong place.

## What is working well

- Destination loading has explicit loading, empty, and retry states, and the form disables generation when there is no valid selection.
- Degraded generation is represented in itinerary metadata and the initial assistant response explains that a saved draft may be incomplete.
- Route quality work already distinguishes estimates and unknown values instead of presenting every detail as verified.
- Sponsored content is modeled separately from ordinary itinerary suggestions, providing a useful foundation for clear disclosure.
- The traveler app has shared design tokens and reusable UI components that can support a focused visual consistency pass.

## Suggested issue sequence

1. Resolve AUDIT-01 and AUDIT-02 as small traveler-facing clarity fixes.
2. Address AUDIT-03 as an accessibility pass through the generation form, including keyboard and focus-state review.
3. Define budget semantics (AUDIT-04) before adding more destination or currency coverage.
4. Review mobile navigation and form/table layouts in the business panel (AUDIT-05).
5. Standardize service failure logging (AUDIT-06) while preserving explicit degraded behavior.
6. Turn the additional product opportunities into scoped design or engineering issues after reviewing the running app.

## Review limits

This document records opportunities for follow-up; it does not create GitHub issues or milestones. The visual review should be refreshed against current running builds before any screenshot-specific design work. Focused accessibility checks, responsive viewport checks, and a guest trip walkthrough would validate the findings during implementation.
