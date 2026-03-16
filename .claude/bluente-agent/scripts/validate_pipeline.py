#!/usr/bin/env python3
"""
Validate a complete bluente-agent pipeline output.

Usage:
    python validate_pipeline.py pipeline_output.json

Expects JSON with keys: signals, leads
"""

import json
import sys
import os

# Add parent paths so we can import sibling validators
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../cross-border-signal-scanner/scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lead-qualifier-and-contact-finder/scripts"))


def check_signals(signals_data: dict) -> tuple[list[str], list[str]]:
    """Basic signal checks (inline for standalone use)."""
    errors, warnings = [], []
    if not signals_data.get("scan_id"):
        errors.append("SIGNALS: 'scan_id' missing")
    signals = signals_data.get("signals", [])
    if isinstance(signals, list) and len(signals) == 0:
        warnings.append("SIGNALS: zero signals")
    return errors, warnings


def check_leads(leads_data: dict) -> tuple[list[str], list[str]]:
    """Basic lead checks (inline for standalone use)."""
    errors, warnings = [], []
    leads = leads_data.get("qualified_leads", [])
    if not isinstance(leads, list):
        errors.append("LEADS: 'qualified_leads' must be an array")
        return errors, warnings
    if len(leads) == 0:
        warnings.append("LEADS: zero qualified leads")
    for i, lead in enumerate(leads):
        prefix = f"LEAD {i+1}"
        for f in ["company_name", "company_domain", "signal_type",
                   "qualification_reason", "contact_name", "contact_linkedin_url"]:
            if not lead.get(f):
                errors.append(f"{prefix}: '{f}' missing or empty")
        if lead.get("contact_verified") is not True:
            errors.append(f"{prefix}: contact not verified")
        li_url = lead.get("contact_linkedin_url", "")
        if li_url and "linkedin.com/in/" not in li_url:
            errors.append(f"{prefix}: contact_linkedin_url doesn't look like a LinkedIn profile URL")
    return errors, warnings


def check_cross_consistency(signals_data, leads_data) -> tuple[list[str], list[str]]:
    """Check signals and leads are consistent."""
    errors, warnings = [], []
    signal_domains = set()
    for sig in signals_data.get("signals", []):
        signal_domains.add(sig.get("company_domain", "").lower())
    for i, lead in enumerate(leads_data.get("qualified_leads", [])):
        domain = lead.get("company_domain", "").lower()
        if signal_domains and domain not in signal_domains:
            warnings.append(f"CROSS: Lead {i+1} domain '{domain}' not found in signals output")
    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_pipeline.py pipeline_output.json")
        print('\nExpected: {"signals": {...}, "leads": {...}}')
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    all_errors = []
    all_warnings = []

    if "signals" in data:
        e, w = check_signals(data["signals"])
        all_errors.extend(e)
        all_warnings.extend(w)
    else:
        all_errors.append("PIPELINE: 'signals' key missing")

    if "leads" in data:
        e, w = check_leads(data["leads"])
        all_errors.extend(e)
        all_warnings.extend(w)
    else:
        all_errors.append("PIPELINE: 'leads' key missing")

    if "signals" in data and "leads" in data:
        e, w = check_cross_consistency(data["signals"], data["leads"])
        all_errors.extend(e)
        all_warnings.extend(w)

    if all_errors:
        print(f"\n{len(all_errors)} ERROR(S):")
        for e in all_errors:
            print(f"  - {e}")
    if all_warnings:
        print(f"\n{len(all_warnings)} WARNING(S):")
        for w in all_warnings:
            print(f"  - {w}")
    if not all_errors and not all_warnings:
        print("\nPipeline output passes all checks.")

    sys.exit(1 if all_errors else 0)


if __name__ == "__main__":
    main()
