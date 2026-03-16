#!/usr/bin/env python3
"""
Validate lead-qualifier-and-contact-finder output.

Usage:
    python validate_leads.py leads.json

Expects a JSON matching the qualifier output schema.
"""

import json
import sys


VALID_URGENCIES = {"hot", "warm", "monitor"}
VALID_SIGNAL_TYPES = {
    "merger_acquisition",
    "international_expansion",
    "regulatory_compliance",
    "cross_border_partnership",
    "new_market_entry",
}


def validate(data: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []

    if not data.get("scan_id"):
        errors.append("'scan_id' missing or empty")

    leads = data.get("qualified_leads", [])
    if not isinstance(leads, list):
        errors.append("'qualified_leads' must be an array")
        return errors, warnings

    if len(leads) == 0:
        warnings.append("Zero qualified leads")

    companies_seen = set()
    for i, lead in enumerate(leads):
        prefix = f"LEAD {i+1}"

        # Required fields
        for f in ["company_name", "company_domain", "signal_type",
                   "signal_evidence", "qualification_reason",
                   "translation_use_case", "contact_name",
                   "contact_linkedin_url"]:
            if not lead.get(f):
                errors.append(f"{prefix}: '{f}' missing or empty")

        # Signal type
        st = lead.get("signal_type", "")
        if st and st not in VALID_SIGNAL_TYPES:
            errors.append(f"{prefix}: invalid signal_type '{st}'")

        # Contact verification
        if lead.get("contact_verified") is not True:
            errors.append(f"{prefix}: contact not verified (contact_verified != true)")

        # LinkedIn URL format
        li_url = lead.get("contact_linkedin_url", "")
        if li_url and "linkedin.com/in/" not in li_url:
            errors.append(f"{prefix}: contact_linkedin_url doesn't look like a LinkedIn profile URL")

        # Urgency
        urgency = lead.get("urgency", "")
        if urgency and urgency not in VALID_URGENCIES:
            errors.append(f"{prefix}: urgency must be one of {VALID_URGENCIES}, got '{urgency}'")

        # Duplicate company check
        domain = lead.get("company_domain", "").lower()
        if domain in companies_seen:
            warnings.append(f"{prefix}: duplicate company_domain '{domain}'")
        companies_seen.add(domain)

        # Qualification quality
        reason = lead.get("qualification_reason", "")
        if reason and len(reason) < 30:
            warnings.append(f"{prefix}: qualification_reason is very short ({len(reason)} chars)")

        use_case = lead.get("translation_use_case", "")
        if use_case and len(use_case) < 20:
            warnings.append(f"{prefix}: translation_use_case is very short ({len(use_case)} chars)")

    # Count consistency
    claimed_qualified = data.get("qualified_count", -1)
    if claimed_qualified >= 0 and claimed_qualified != len(leads):
        errors.append(f"qualified_count ({claimed_qualified}) != actual leads count ({len(leads)})")

    disqualified = data.get("disqualified", [])
    claimed_disqualified = data.get("disqualified_count", -1)
    if claimed_disqualified >= 0 and claimed_disqualified != len(disqualified):
        errors.append(f"disqualified_count ({claimed_disqualified}) != actual disqualified count ({len(disqualified)})")

    # Disqualified entries should have reasons
    for i, dq in enumerate(disqualified):
        if not dq.get("disqualification_reason"):
            warnings.append(f"DISQUALIFIED {i+1}: missing disqualification_reason")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_leads.py leads.json")
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
        print("\nLead qualifier output passes all checks.")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
