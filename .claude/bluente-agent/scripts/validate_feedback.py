#!/usr/bin/env python3
"""
Validate feedback parsing results.

Usage:
    python validate_feedback.py feedback.json

Expects JSON with keys: actions (array of parsed actions)
"""

import json
import sys

VALID_ACTIONS = {"approve", "reject", "more_on", "watch"}


def validate(data: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []

    actions = data.get("actions", [])
    if not isinstance(actions, list):
        errors.append("'actions' must be an array")
        return errors, warnings

    if len(actions) == 0:
        warnings.append("No actions parsed from feedback")

    for i, action in enumerate(actions):
        prefix = f"ACTION {i+1}"
        atype = action.get("type", "")
        if atype not in VALID_ACTIONS:
            errors.append(f"{prefix}: invalid type '{atype}', must be one of {VALID_ACTIONS}")

        if atype in ("approve", "reject", "more_on"):
            refs = action.get("lead_numbers", [])
            if not refs:
                errors.append(f"{prefix}: '{atype}' action missing lead_numbers")
            for r in refs:
                if not isinstance(r, int) or r < 1:
                    errors.append(f"{prefix}: invalid lead number {r}")

        if atype == "reject" and not action.get("reason"):
            warnings.append(f"{prefix}: rejection without reason")

        if atype == "watch" and not action.get("company"):
            errors.append(f"{prefix}: 'watch' action missing company name")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_feedback.py feedback.json")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    errors, warnings = validate(data)

    if errors:
        print(f"\n{len(errors)} ERROR(S):")
        for e in errors:
            print(f"  - {e}")
    if warnings:
        print(f"\n{len(warnings)} WARNING(S):")
        for w in warnings:
            print(f"  - {w}")
    if not errors and not warnings:
        print("\nFeedback parsing passes all checks.")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
