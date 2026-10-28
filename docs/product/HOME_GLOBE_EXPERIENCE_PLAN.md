# Interactive Home Globe — experience and implementation plan

**Status:** Proposal, 2026-10-29. No globe code, dependency, image, or texture has been added yet.

## Product goal

Give the traveler home page a memorable sense of exploration: a slowly moving Earth, a small set of beautiful landscape stories, and a clear path from a supported place to the existing trip form. The home page must remain quick to open and easy to use when 3D rendering is unavailable.

The [current home page](../../frontend/src/pages/home/HomePage.tsx) has a centered welcome panel, a destinations list from the API, and a form overlay. The [destination registry](../../backend/app/core/destination_registry.py) currently enables **Kyrgyzstan only**. The globe must not suggest that trips can be generated worldwide. Landscape stories can illustrate Kyrgyzstan now; other countries can be added only with an explicit preview label or after their destination contracts are enabled.

## Recommended experience

### Opening view

- Keep the heading, supported-destination message, and primary **Create a trip** action above the 3D layer. Put the globe in the right/background portion of the hero on wide screens, with a subtle dark-to-light overlay behind text. The globe should look like a product feature, not an opaque full-screen video.
- Start with one of three to five **curated Kyrgyzstan scenes** selected at random per page visit (possible subjects: Issyk-Kul, Ala-Archa, and the Karakol area). Randomize the scene and starting globe viewpoint, not an unreviewed live image search. Avoid repeating the same scene immediately when local preference data is available.
- Show one compact scene card with the location name, a landscape photo, photographer/source credit, and an **Explore this place** button. A marker on the globe identifies the active scene. The card can be dismissed without blocking the main trip action.
- A scene card is *inspiration*, not a verified itinerary stop, live offer, or proof that every place is supported by planning data.

### Interaction

| Input | Behavior |
|---|---|
| Mouse drag / touch drag | Rotate the globe; stop automatic rotation while the traveler interacts. |
| Mouse wheel / trackpad | Preserve normal page scrolling by default. Offer explicit zoom buttons and allow wheel zoom only in a clearly labeled **Explore globe** interaction mode. |
| Marker click / scene card | Rotate to that scene, update its card, and expose **Create a trip to Kyrgyzstan** only when its destination ID is present in the enabled destinations API response. |
| Keyboard / assistive tech | Use an ordinary list of scene buttons and zoom/rotate controls as an equivalent path; the canvas itself is decorative to screen readers. |
| Form open | Stop globe interaction and animation so the planning form has a calm, stable backdrop. |

Do not generate a trip directly from a globe click. A click should select a scene, then open the existing form with the supported destination preselected. The form still collects days, budget preference, interests, and the travel brief. With the current API there is only one enabled destination, so scene variation comes from landscapes within Kyrgyzstan rather than a world-spanning destination catalogue.

### Layout by device

- **Desktop:** large globe right of the copy; scene card near the marker or at the bottom edge; hero content remains readable at 200% zoom.
- **Tablet:** smaller globe and a card below the headline; avoid overlap with the sidebar or create button.
- **Phone:** show a poster frame and scene cards first. Load interactive 3D only after an explicit **Explore globe** tap or after a measured device-capability gate. The trip form must never depend on the canvas.
- **Reduced motion:** no automatic rotation or animated camera travel. Keep scene selection and the static image available. Honor `prefers-reduced-motion` as described by [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-reduced-motion).

## Globe technology and asset choice

| Candidate | Strength | Trade-off | Decision |
|---|---|---|---|
| [react-globe.gl](https://github.com/vasturiano/react-globe.gl) | Existing React wrapper around Three.js/WebGL; supports image-wrapped Earth, point clicks, camera movement, and render pause/resume. The package declares an MIT license and React peer dependency. | Larger rendering stack and texture cost; requires careful lazy loading and device checks. | **Prototype first** for the desired Earth look and marker interaction. |
| [COBE](https://github.com/shuding/cobe) | MIT-licensed, dependency-light, approximately 5 KB according to its project; attractive abstract globe with markers. | Stylized dot-map appearance rather than a photographic Earth; custom work for location picking and accessible controls. | Fallback candidate if the visual concept can be more abstract or the first prototype misses performance targets. |
| Custom Three.js scene | Maximum visual control. | More shader, interaction, cleanup, and accessibility work for an effect that existing libraries already provide. | Defer. |

The proposed Earth texture is a compressed, appropriately sized derivative of [NASA Blue Marble: Next Generation](https://science.nasa.gov/earth/earth-observatory/blue-marble-next-generation/), served with the app rather than pulled from an uncontrolled demo URL. NASA asks users to credit **NASA Earth Observatory**; its [media guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/) also require checking for third-party material and avoiding implied endorsement. Keep a source URL and attribution in the asset manifest and visible credits.

For landscapes, select a small set of specific images and record each photo ID, photographer, source URL, subject, license snapshot, and optimized image sizes. [Pexels permits use on websites and apps](https://www.pexels.com/license/); its [API guidelines](https://www.pexels.com/api/documentation/) call for a prominent Pexels link when making API requests and photographer credit where possible. Use curated images for the home page so a random API response cannot mismatch a location or create unstable loading. Never label a generic photo as an exact place without checking its metadata.

## Integration design

1. Add a `home-globe` widget that owns the canvas, camera, marker selection, and cleanup. Keep `HomePage` responsible for the form, destination query, and navigation.
2. Use a small curated `GlobeScene` manifest with `id`, `destinationId`, display location, reviewed latitude/longitude, image variants, alt text, source, photographer, and attribution. Treat the manifest as editorial data, not as a second destination registry.
3. Intersect scene `destinationId` with the enabled destinations returned by `useDestinationsQuery()`. If absent, show a clearly labeled inspiration card without a trip-creation CTA.
4. Lazy-load the 3D widget after the basic home content is usable. Render a CSS/poster fallback immediately and retain it on WebGL failure, context loss, reduced-motion preference, or device exclusion.
5. On scene selection, update React state and point the globe camera at the reviewed coordinates. Opening the form passes `destinationId` into `GenerateTripForm`; the form verifies it against the destinations API and retains its existing validation and submission path.
6. Stop rendering when the tab is hidden, the globe is outside the viewport, or the form is open; release WebGL resources on unmount. `react-globe.gl` exposes camera controls and `pauseAnimation`/`resumeAnimation`, but its pause also disables interaction, so resume on an explicit wrapper interaction before accepting globe input. See its [API reference](https://github.com/vasturiano/react-globe.gl#readme).

## Performance gates for the prototype

These are **proposed targets**, not measured results. Record baseline home-page metrics before adding the globe, then compare the prototype on a mid-range laptop and phone with CPU throttling and a slow connection.

- Basic heading, destination status, and Create action appear without waiting for the 3D package or texture.
- Keep the initial route's transferred JavaScript increase below **50 KB compressed**; load the globe in a separate chunk only when needed. Record the actual chunk and texture transfer sizes in the PR.
- Target at least **45 frames per second** during desktop dragging and **30 frames per second** in the phone's opt-in 3D mode on the selected reference devices. Keep button-to-response time under **200 ms** and inspect long tasks in browser profiling. Record the device models and profiling method alongside results.
- Cap the canvas pixel ratio (start at `min(devicePixelRatio, 1.5)`), limit texture resolution and marker count, and avoid post-processing, atmosphere particles, or continuous photo transitions in the first version. [MDN's WebGL guidance](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices) recommends smaller back buffers and explicit memory budgeting on varying devices.
- Keep only one WebGL context. Pause or unmount it when hidden, and fall back to the poster when initialization fails. Check memory and context behavior after repeated home/form/trip navigation.
- If the quality or performance gates fail, ship the static scene-card experience and evaluate COBE before revisiting a richer renderer.

## Suggested delivery sequence

1. **Design prototype:** two desktop compositions and one mobile composition using the current home copy and sidebar; decide globe placement, lighting, overlay, and scene-card states.
2. **Asset review:** choose the exact Earth texture and three to five landscape photos; document rights, credits, place accuracy, dimensions, and fallback poster.
3. **Technical spike:** integrate `react-globe.gl` in an isolated page or branch; measure transfer size, first render, drag smoothness, memory, and WebGL failure handling against the gates above.
4. **Home integration:** connect supported destination IDs, scene selection, form preselection, reduced-motion behavior, keyboard controls, and responsive layout.
5. **Review:** check contrast, 200% zoom, touch scrolling, keyboard path, no-WebGL fallback, slow connection, and realistic image loading. Compare a before/after capture on desktop and phone.

This plan does not add an issue or milestone yet. Once the visual prototype and asset choices are reviewed, the work can be split into reviewable issues for assets, the globe widget, and home-page integration.
