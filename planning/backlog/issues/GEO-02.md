## Context

Sponsored places currently use a city and coordinates, while business-panel location picking and validation assume Kyrgyzstan. Admin moderation and matching must remain trustworthy when more than one country is enabled. See `businessPanel/src/features/business/sponsored-places/` and `backend/app/services/sponsored_injection_service.py`.

## Goal

Enable country-scoped business locations and sponsored matching while preserving existing Kyrgyzstan partners, approval state, and analytics.

## Scope

- Add explicit country/region fields to sponsored business locations and migrate existing locations to `KG` without changing approval/active state.
- Make the business location picker, phone/contact guidance, and address validation use the chosen enabled country rather than fixed KG bounds.
- Validate country/location association on the backend; frontend-only boundaries are insufficient.
- Match sponsored places by country first, then compatible region/geographic proximity and category; reject textual same-city false matches.
- Update admin moderation views and analytics to show country/region context.
- Preserve visibly sponsored labeling, approval controls, frequency cap, and interaction/impression reporting.

## Acceptance criteria

- Every existing sponsored place is migrated to `KG` and remains editable/moderated with its current status.
- A new location cannot be saved with coordinates inconsistent with its selected country.
- A sponsored place is never injected into a trip from a different country, even when city names match.
- Admins can review the location and country before approval; unapproved/inactive entries never appear.
- Business reporting remains scoped to the owning business and can distinguish market/country.

## Technical touchpoints

- `backend/app/models/sponsored_place.py` and Alembic migrations
- `backend/app/schemas/sponsored_place.py`
- `backend/app/services/sponsored_place_service.py`
- `backend/app/services/sponsored_injection_service.py`
- `backend/app/services/admin_moderation_service.py`
- `businessPanel/src/features/business/sponsored-places/`
- Admin moderation and analytics features in `businessPanel/src/features/admin/`

## Dependencies and research

- Depends on DEST-01 and the enabled destination catalogue from DEST-02.
- Decide market-specific address/contact validation only after reviewing local operational requirements.

## Out of scope

- Changing the ad pricing model or removing sponsored labels.
- Enabling every country at once.

## Verification

Cover the existing KG migration, cross-country same-city matching, out-of-country coordinate rejection, moderation/approval, interaction analytics, and business ownership boundaries.
