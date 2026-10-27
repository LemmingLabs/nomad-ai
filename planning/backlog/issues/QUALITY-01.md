## Context

The traveler home page uses broad “where you want to go” language, while trip generation only offers destinations currently supported by the app. The current welcome state also gives a first-time guest little indication of what a generated trip contains.

## Goal

Set accurate expectations before a traveler opens the trip form and make the currently supported destination options easy to discover.

## Acceptance criteria

- Home page copy does not imply unsupported destinations are available.
- The currently supported destinations are shown or clearly discoverable before or within the create-trip entry point.
- Destination labels come from the existing destinations API/catalogue rather than a second hard-coded list.
- The home empty state gives a concise example or preview of the kind of itinerary the app creates.
- Loading, empty, and destination-service failure states remain understandable and do not block access to the existing trip list.

## Verification

Review the guest and authenticated home screen, including loading and failed destination data. Confirm the displayed destination list matches the trip form.
