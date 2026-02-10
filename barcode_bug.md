# Barcode Camera Black Screen Postmortem

## Summary
The barcode scanner page showed a black or empty camera region even after the loading message cleared. The issue was reproducible on desktop browsers using the html5-qrcode path. The fix was to programmatically start the camera via `Html5Qrcode` and avoid hiding the scanner placeholder image indiscriminately.

## Impact
- Users could not scan barcodes on desktop because the camera preview never rendered.
- The UI appeared ready (loading overlay cleared) but the scan area was blank.

## Timeline
- Initial symptom: React warning about maximum update depth in `app/barcode/page.tsx`.
- After removing the update loop, camera still showed a black/blank preview.
- Observed that html5-qrcode created a hidden placeholder image and no `<video>` element.
- Root causes identified and addressed.

## Root Cause
1) html5-qrcode was instantiated with `Html5QrcodeScanner`, which requires a manual Start action. The dashboard was hidden via CSS, so the Start button never appeared and the `<video>` element was never created.
2) CSS hid all data-image `<img>` elements inside the scanner container, which removed the library's placeholder image and masked the lack of an actual video element.
3) There was earlier double initialization of camera permissions, which contributed to confusing logs and retries.

## Resolution
- Switched from `Html5QrcodeScanner` to `Html5Qrcode` and invoked `start()` programmatically.
- Scoped CSS to hide only the info icon watermark instead of all data-image `<img>` tags.
- Reduced console noise and guarded initialization state to avoid a stuck scanner.

## Lessons Learned
- If a library expects a UI-driven start action, hiding that UI can prevent core functionality.
- Broad CSS selectors that hide elements by data URLs can accidentally remove functional or diagnostic UI.
- Camera initialization paths should be single-owner and explicit.

## Follow-Up Actions
- Consider adding a readiness check that asserts a `<video>` element exists after initialization.
- Add a small UI hint when camera initialization fails to surface state clearly.
