#!/usr/bin/env python3
"""
Validates commit messages according to Conventional Commits specification.

This script is used as a pre-commit hook to enforce commit message standards.
It is called automatically by the pre-commit framework during the commit-msg stage.

The validator automatically filters out git comment lines (lines starting with #)
which are ignored by git when processing commits. This prevents git's automatic
comment template from interfering with validation.

Usage:
    python scripts/commit-msg-validator.py <commit-msg-file>

Called by pre-commit with:
    python scripts/commit-msg-validator.py $1

Where:
    $1 = Path to the commit message file (provided by pre-commit)

Requirements:
    - Subject line: type(scope): description
    - Type must be one of: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert
    - Subject: max 50 characters, no trailing period
    - Body: required, max 72 characters per line, ends with period
    - Blank line between subject and body
    - Git comments (starting with #) are automatically filtered

Examples:
    ✓ feat: add user authentication

      Added user authentication system with login endpoints.
      Uses JWT for session management.

    ✓ fix(api): handle null responses

      Fixed issue where null API responses caused crashes.
      Now properly validates response data.
"""

import re
import sys

# Conventional commit types
VALID_TYPES = {
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "chore",
    "ci",
    "build",
    "revert",
}

# Rules
MAX_HEADER_LENGTH = 50
MAX_BODY_LINE_LENGTH = 72
BREAKING_CHANGE_PATTERN = r"^BREAKING[\s-]CHANGE"


def validate_commit_message(message: str) -> tuple[bool, str]:
    """
    Validate commit message against Conventional Commits specification.

    This function is called during the pre-commit hook process to ensure
    all commit messages follow the project's commit message standards.

    Args:
        message: The full commit message text from the commit-msg file

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: Boolean indicating if the message passed all checks
        - error_message: Detailed error message if validation failed, empty string if valid
    """
    # Remove git comment lines (starting with #) which are ignored by git
    lines_raw = message.split("\n")
    lines = [line for line in lines_raw if not line.startswith("#")]

    # Rejoin and strip leading/trailing whitespace
    message_clean = "\n".join(lines).strip()
    lines = message_clean.split("\n")

    if not lines:
        return False, "Commit message cannot be empty"

    header = lines[0]

    # Parse header: type(scope): subject
    match = re.match(r"^(\w+)(?:\(([^)]*)\))?!?:\s(.+)$", header)
    if not match:
        return False, (
            "Invalid commit message format.\n"
            "Expected: type(scope): subject\n"
            f"Example: feat(auth): add login endpoint\n\n"
            f"Got: {header}"
        )

    commit_type, scope, subject = match.groups()

    # Validate type
    if commit_type not in VALID_TYPES:
        return False, (
            f"Invalid commit type: {commit_type}\n"
            f"Valid types: {', '.join(sorted(VALID_TYPES))}"
        )

    # Validate header length
    if len(header) > MAX_HEADER_LENGTH:
        return False, (
            f"Commit header is too long ({len(header)} > {MAX_HEADER_LENGTH})\n"
            f"Current: {header}\n"
            f"Maximum length is {MAX_HEADER_LENGTH} characters"
        )

    # Validate subject doesn't end with period
    if subject.endswith("."):
        return False, "Subject line should not end with a period"

    # Check for body requirement
    if len(lines) < 3:
        return False, (
            "Commit body is required.\n"
            "Format:\n"
            "  type(scope): subject\n"
            "  \n"
            "  Detailed explanation of the change\n"
            "  Why this change is needed, what it fixes, etc."
        )

    # Check for blank line between header and body
    if lines[1].strip() != "":
        return False, "There must be a blank line between subject and body"

    # Validate body is not empty
    body = "\n".join(lines[2:]).strip()
    if not body:
        return False, "Commit body cannot be empty"

    # Validate body ends with period
    if not body.endswith("."):
        return False, "Commit body must end with a period"

    # Validate body line length
    body_lines = lines[2:]
    for i, line in enumerate(body_lines, start=1):
        if len(line) > MAX_BODY_LINE_LENGTH:
            return False, (
                f"Line {i + 2} of commit message is too long ({len(line)} > {MAX_BODY_LINE_LENGTH})\n"
                f"Body line: {line[:50]}...\n"
                f"Maximum line length is {MAX_BODY_LINE_LENGTH} characters"
            )

    return True, ""


def main():
    """
    Entry point for the commit message validator.

    Called automatically by the pre-commit framework during the commit-msg stage.
    The pre-commit hook passes the path to the commit message file as an argument.

    Exit codes:
        0 - Commit message is valid
        1 - Commit message is invalid (validation failed)
    """
    if len(sys.argv) < 2:
        print("Usage: commit-msg-validator <commit-msg-file>", file=sys.stderr)
        print(
            "\nNote: This script is typically called by pre-commit, not manually.",
            file=sys.stderr,
        )
        print(
            "To run manually: python scripts/commit-msg-validator.py /path/to/commit/msg",
            file=sys.stderr,
        )
        sys.exit(1)

    commit_msg_file = sys.argv[1]

    try:
        with open(commit_msg_file, "r") as f:
            message = f.read()
    except Exception as e:
        print(f"Error reading commit message file: {e}", file=sys.stderr)
        sys.exit(1)

    is_valid, error_msg = validate_commit_message(message)

    if not is_valid:
        print(f"\n❌ Invalid commit message:\n\n{error_msg}\n", file=sys.stderr)
        sys.exit(1)

    print("✓ Commit message is valid")
    sys.exit(0)


if __name__ == "__main__":
    main()
