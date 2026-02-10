# AI Instructions

## Migrations and Tests
- When making changes that require migrations, generate and apply migrations before completing the request.
- Run the test suite after changes and report results (including skips or failures).

## Change Notes
- When adding any notable feature, record it in `CHANGE_NOTES.md` and include decisions, edge cases, unique scenarios, deletions, and anything that didn’t work.
- For every feature, add both unit tests and e2e tests using the current pytest setup, and document the test cases in `CHANGE_NOTES.md` under a Tests subsection for that feature.
