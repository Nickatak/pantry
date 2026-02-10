# Patch Notes

**Dashboard and UX**
- Compact dashboard view with sticky search/actions bar, category filter, and bigger touch targets.
  Decision: sticky bar keeps controls accessible while scrolling in fast-paced use.
- Quantity badges on item cards/rows and inline quantity controls (compact + expanded views).
  Decision: minimum quantity is 1; decrement disabled at 1; input is clamped.
**Tests**
- `/api/items/` lists owned items only and supports quantity updates.
- E2E UPC lookup exercises item creation and listing behavior.

**User-Owned Items**
- User-owned item tracking via `UserItemQuantity`, and user-scoped item listings.
  Decision: list is filtered by ownership; delete removes user link and deletes item only if no users remain.
- User item routes:
  - `POST /api/items/{id}/add-to-user/` creates with 1 or increments.
  - `PATCH /api/items/{id}/quantity/` updates quantity.
  Edge cases: quantity endpoint rejects non-integers and values < 1; add-to-user accepts optional `location_id` and defaults to Pantry.
**Tests**
- `POST /api/items/{id}/add-to-user/` creates/increments quantity with DB verification.
- `/api/items/` returns only authenticated user’s items.
- `PATCH /api/items/{id}/quantity/` updates quantity and rejects invalid values.

**Locations**
- Added `Location` model (per-user) with default locations created at user signup: Pantry, Fridge, Freezer, Kitchen Counter.
  Decision: defaults are auto-created on user creation; migration backfills defaults for existing users.
- `UserItemQuantity` now ties to a specific location (quantity is per location).
  Edge case: existing user-item quantities are migrated to Pantry.
- Item list totals quantity across all locations for the user.
  Decision: dashboard shows aggregate quantity, not per-location breakdown yet.
- Added locations API (`GET /api/locations/`, `POST /api/locations/`) to support selection from the UI.
  Decision: list is user-scoped; create returns 200 if the name already exists.
  Edge case: missing name returns 400.
**Tests**
- Default locations are created on user signup.
- Add-to-user defaults to Pantry and increments.
- Listing sums quantities across locations.
- Quantity update targets a specific location via `location_id`.
- `Location` uniqueness: same user name duplicates fail; different users can share the same name.
- Add-to-user and quantity update work with `location_id` provided.
- Locations API: list returns defaults; create adds a new location for the user.

**Barcode Flow**
- Barcode item creation now adds the created item to the user automatically.
  Edge case: if add-to-user fails, item is created but not owned (follow-up if you want rollback).
  Unique scenario: add-to-user now expects a JSON body (empty or with `location_id`) to avoid JSON parser errors.
- Location selection added for barcode item adds, passing `location_id` to add-to-user when chosen.
  Decision: default selection is Pantry when available.
**Tests**
- E2E: barcode flow uses selected location id when calling add-to-user.
- Unit: ItemViewSet default location helper creates/returns Pantry when no location is set.

**Deletions**
- None.

**Things That Didn’t Work / Follow-Ups**
- No rollback yet when item creation succeeds but add-to-user fails; add if you want atomic behavior.
- Posting to add-to-user without a JSON body caused a parse error; resolved by sending `{}` from the client.
- Unit tests initially attempted to create duplicate default locations; adjusted to use pre-created defaults from the user creation signal.
- Duplicate-location unit test now wraps the IntegrityError in a transaction to avoid leaving the test DB in a broken state.
