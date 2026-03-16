#!/usr/bin/env python3
"""
Check Supabase for existing company domains (dedup helper).

Usage:
    python supabase_dedup.py domain1.com domain2.com ...

Prints which domains already exist in bluente_leads table.
Requires SUPABASE_URL and SUPABASE_KEY environment variables.
"""

import json
import os
import sys
import urllib.request
import urllib.error


def check_domains(domains: list[str]) -> dict[str, bool]:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        print("Warning: SUPABASE_URL or SUPABASE_KEY not set. Skipping dedup.", file=sys.stderr)
        return {d: False for d in domains}

    results = {}
    for domain in domains:
        api_url = f"{url}/rest/v1/bluente_leads?company_domain=eq.{domain}&select=company_domain&limit=1"
        req = urllib.request.Request(api_url, headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
        })
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
                results[domain] = len(data) > 0
        except urllib.error.URLError:
            results[domain] = False

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python supabase_dedup.py domain1.com domain2.com ...")
        sys.exit(1)

    domains = sys.argv[1:]
    results = check_domains(domains)

    for domain, exists in results.items():
        status = "EXISTS" if exists else "NEW"
        print(f"  {status}: {domain}")


if __name__ == "__main__":
    main()
