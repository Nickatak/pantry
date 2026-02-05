# Commit Message Guidelines

This project uses **Semantic Versioning** with **Conventional Commits** to manage version numbers and track changes.

## Semantic Versioning

Given a version number MAJOR.MINOR.PATCH, increment the:

1. **MAJOR** version when you make incompatible API changes
2. **MINOR** version when you add functionality in a backward-compatible manner
3. **PATCH** version when you make backward-compatible bug fixes

Reference: https://semver.org/

## Conventional Commits

Commit messages MUST follow the Conventional Commits format to automatically map to semantic versioning:

### Format

```
<type>[optional scope]: <description>

<body>

[optional footer(s)]
```

**Requirements:**
- A commit body is **REQUIRED** - explain what changed and why
- Subject line must **NOT** end with a period
- Commit body must **end with a period**
- Maximum subject line length: 50 characters
- Maximum body line length: 72 characters

### Type

The commit type determines the version bump:

- **feat**: A new feature (MINOR version bump)
- **fix**: A bug fix (PATCH version bump)
- **BREAKING CHANGE**: Breaking API changes (MAJOR version bump) - Use in footer
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring without changing functionality
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Dependency updates, build process changes, etc.
- **ci**: CI/CD configuration changes
- **build**: Changes to build system or dependencies
- **revert**: Revert a previous commit

### Scope (Optional)

A scope may be provided after the type to provide additional context:

```
feat(auth): add login endpoint
fix(api): handle null responses
```

### Examples

**New Feature (MINOR):**
```
feat(dashboard): add user profile section

Added a new profile section to the dashboard that displays user information
including name, email, and account creation date. This improves user experience
by providing a dedicated space for profile management.
```

**Bug Fix (PATCH):**
```
fix(api): correctly handle auth token expiration

Fixed an issue where expired authentication tokens were not properly refreshed,
causing users to be unexpectedly logged out. The token refresh logic now checks
expiration time before making API requests.
```

**Breaking Change (MAJOR):**
```
feat(api)!: change response format from XML to JSON

BREAKING CHANGE: API responses are now returned as JSON instead of XML.
Clients must update their parsing logic to handle JSON format.

This change improves performance and reduces payload size compared to XML.
All API endpoints have been updated to return JSON responses.
```

**Other Examples:**
```
docs: update README with setup instructions

Updated the README to include detailed setup instructions for new developers,
including Python virtual environment setup, dependency installation, and
running the development servers.
```

```
chore(deps): update Next.js to v15

Upgraded Next.js dependency from v14 to v15 to get latest performance
improvements and security patches.
```

```
refactor(auth): improve token validation logic

Simplied the token validation code by extracting common logic into a reusable
utility function. This reduces code duplication and improves maintainability.
```

```
test(e2e): add login flow tests

Added comprehensive end-to-end tests for the user login flow, including
successful login, invalid credentials, and session handling scenarios.
```

## Pre-commit Validation

Commit messages are validated automatically via pre-commit hook when you commit. Invalid messages will prevent commits with a descriptive error message explaining what needs to be fixed.

Example validation failure:

```
❌ Invalid commit message:

Commit body must end with a period
```

The validator will provide specific feedback on what rule was violated and how to fix it.

## Invalid Examples

These commits will be rejected:

```
❌ add new feature
   (missing type and colon)

❌ Feat: add login
   (type should be lowercase)

❌ feat: add login.
   (subject should not end with period)

❌ feat: add very long feature that exceeds the maximum character limit of fifty characters
   (header too long)

❌ feat: add login
   (missing body)

❌ feat: add login
   fix: another commit
   (missing blank line before body)

❌ feat: add login

   Added login functionality
   (body must end with period)

❌ feat: add login

   This is a very long line in the commit body that exceeds the maximum allowed character limit of seventy-two characters.
   (body line too long - max 72 characters)
```

## Valid Examples

These commits will be accepted:

```
feat: add user authentication

Added user authentication system with login and registration endpoints.
Includes JWT token-based session management and password hashing.
```

```
fix(dashboard): resolve loading spinner issue

Fixed a bug where the loading spinner remained visible even after data
was successfully loaded from the API.
```

```
docs: update install instructions

Updated installation documentation with the latest setup steps and
system requirements.
```

```
refactor(api): improve error handling

Refactored error handling across API endpoints to use consistent
error response format and logging.
```

```
chore(deps): upgrade dependencies

Updated development and production dependencies to their latest stable
versions for security patches and performance improvements.
```
