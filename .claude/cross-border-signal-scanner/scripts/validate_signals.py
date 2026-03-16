#!/usr/bin/env python3
"""
Validate cross-border-signal-scanner output.

Usage:
    python validate_signals.py signals.json

Expects a JSON matching the scanner output schema.
"""

import json
import sys


VALID_SIGNAL_TYPES = {
    "merger_acquisition",
    "international_expansion",
    "regulatory_compliance",
    "cross_border_partnership",
    "new_market_entry",
}

VALID_SCAN_MODES = {"daily", "webhook", "targeted"}


def validate(data: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []

    # Top-level fields
    if not data.get("scan_id"):
        errors.append("'scan_id' missing or empty")

    scan_mode = data.get("scan_mode")
    if scan_mode not in VALID_SCAN_MODES:
        errors.append(f"'scan_mode' must be one of {VALID_SCAN_MODES}, got '{scan_mode}'")

    if not data.get("scan_timestamp"):
        errors.append("'scan_timestamp' missing or empty")

    signals = data.get("signals", [])
    if not isinstance(signals, list):
        errors.append("'signals' must be an array")
        return errors, warnings

    if len(signals) == 0:
        warnings.append("Zero signals returned")
        return errors, warnings

    domains_seen = set()
    for i, sig in enumerate(signals):
        prefix = f"SIGNAL {i+1}"

        # Required fields
        for f in ["company_name", "company_domain", "signal_type",
                   "signal_evidence", "reasoning"]:
            if not sig.get(f):
                errors.append(f"{prefix}: '{f}' missing or empty")

        # Signal type validation
        st = sig.get("signal_type", "")
        if st and st not in VALID_SIGNAL_TYPES:
            errors.append(f"{prefix}: invalid signal_type '{st}'")

        # Scoring validation
        for axis in ["urgency", "relevance", "translation_likelihood"]:
            val = sig.get(axis)
            if not isinstance(val, (int, float)):
                errors.append(f"{prefix}: '{axis}' must be a number, got {type(val).__name__}")
            elif not (1 <= val <= 10):
                errors.append(f"{prefix}: '{axis}'={val}, must be 1-10")

        # Composite check
        u = sig.get("urgency", 0)
        r = sig.get("relevance", 0)
        t = sig.get("translation_likelihood", 0)
        expected = u * r * t
        actual = sig.get("composite", 0)
        if isinstance(u, (int, float)) and isinstance(r, (int, float)) and isinstance(t, (int, float)):
            if abs(expected - actual) > 1:
                errors.append(f"{prefix}: composite math wrong: {actual} != {expected}")

        if isinstance(actual, (int, float)) and actual < 100:
            warnings.append(f"{prefix}: low composite ({actual}) -- weak signal")

        # Evidence quality
        evidence = sig.get("signal_evidence", "")
        if evidence and len(evidence) < 30:
            warnings.append(f"{prefix}: signal_evidence is very short ({len(evidence)} chars)")

        # Domain dedup within batch
        domain = sig.get("company_domain", "").lower()
        if domain in domains_seen:
            warnings.append(f"{prefix}: duplicate company_domain '{domain}' in batch")
        domains_seen.add(domain)

    # Aggregate checks
    raw = data.get("raw_signals_found", 0)
    after = data.get("after_dedup", 0)
    if isinstance(raw, int) and isinstance(after, int) and after > raw:
        errors.append(f"after_dedup ({after}) > raw_signals_found ({raw})")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_signals.py signals.json")
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
        print("\nSignal scanner output passes all checks.")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
