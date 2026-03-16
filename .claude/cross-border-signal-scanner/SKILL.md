---
name: cross-border-signal-scanner
description: "Scans for companies showing cross-border business signals indicating translation needs. Outputs scored, deduped signals. TRIGGERS: (1) Daily cron scan, (2) Parallel webhook with structured signal data, (3) Targeted account monitoring request ('watch {company}'). This is Skill 1 in the pipeline -- its output feeds into lead-qualifier-and-contact-finder."
---

# Cross-Border Signal Scanner

> **Find companies that just created a translation need they might not know they have yet.** The best signals are recent, specific, and verifiable -- not vague industry trends.

## What This Does

Scans public sources for companies showing cross-border business activity: M&A, international expansion, regulatory compliance, partnerships, and new market entry. Each signal is scored on urgency, relevance to translation, and likelihood of document translation need. Output is deduped against previously surfaced companies in Supabase.

---

## Three Modes

### Mode 1: Daily Web Scan

Search the web for fresh cross-border signals from the past 24 hours using optimized queries per signal type. See `references/web-search-patterns.md` for query templates.

**Process:**
1. Run 2-3 search queries per signal type (5 types = 10-15 queries)
2. Extract company name, domain, signal evidence from results
3. Score each signal
4. Dedup against Supabase `bluente_leads` table (check `company_domain`)
5. Return top signals sorted by composite score

### Mode 2: Parallel Webhook Parse

Receive a structured webhook payload from Parallel (or similar signal provider). Parse the payload, extract relevant signals, and score them.

**Process:**
1. Parse the webhook payload (see `references/parallel-webhook-format.md`)
2. Map payload fields to signal schema
3. Score and dedup
4. Return scored signals

### Mode 3: Targeted Account Monitoring

Anthony requests monitoring of a specific company: `watch Globex Industries` or `scan globex.com`.

**Process:**
1. Search for the specific company across all signal types
2. Pull recent news, press releases, job postings
3. Score any cross-border signals found
4. Return all signals (even low-scoring ones) since this is a targeted request

---

## Signal Types

See `references/signal-types.md` for detailed definitions, search queries, and evidence patterns for each type:

1. **Mergers & Acquisitions** (cross-border M&A)
2. **International Expansion** (new offices, market entry)
3. **Regulatory Compliance** (multilingual documentation requirements)
4. **Cross-Border Partnerships** (JVs, distribution, licensing)
5. **New Market Entry** (product launches in new geographies)

---

## Scoring

Each signal is scored on three axes (1-10 each):

| Axis | What it measures | High score example | Low score example |
|------|-----------------|-------------------|------------------|
| `urgency` | How time-sensitive is the translation need? | M&A closing in 30 days | Company "considering" international expansion |
| `relevance` | How likely does this signal produce documents needing translation? | Legal merger requiring contract translation in 3 languages | Company hired 1 remote employee abroad |
| `translation_likelihood` | How likely is this company to need a formatting-preserving solution specifically? | Complex PDFs (legal, financial, technical) | Simple web content only |

**Composite** = `urgency` x `relevance` x `translation_likelihood`

- **500+**: Strong signal, prioritize
- **200-499**: Moderate signal, worth surfacing
- **100-199**: Weak signal, surface only if few strong ones
- **Below 100**: Skip unless targeted scan

---

## Output Schema

```json
{
  "scan_id": "uuid",
  "scan_mode": "daily | webhook | targeted",
  "scan_timestamp": "ISO 8601",
  "query_target": "null | company_name for targeted scans",
  "signals": [
    {
      "company_name": "Globex Industries",
      "company_domain": "globex.com",
      "signal_type": "merger_acquisition | international_expansion | regulatory_compliance | cross_border_partnership | new_market_entry",
      "signal_evidence": "Globex Industries announced acquisition of Tokyo-based Yamada Corp for $450M, expanding into Japanese manufacturing market. Deal expected to close Q2 2026.",
      "source_url": "https://example.com/article",
      "urgency": 8,
      "relevance": 9,
      "translation_likelihood": 8,
      "composite": 576,
      "detected_languages": ["English", "Japanese"],
      "document_types_likely": ["legal contracts", "compliance filings", "internal communications"],
      "reasoning": "Cross-border M&A requires extensive legal and compliance documentation in both languages. Complex financial and legal PDFs are core to this process."
    }
  ],
  "raw_signals_found": 15,
  "after_dedup": 8,
  "dedup_method": "supabase_company_domain"
}
```

---

## Dedup Logic

Before returning signals, check each `company_domain` against the Supabase `bluente_leads` table:

```sql
SELECT company_domain FROM bluente_leads WHERE company_domain = $1;
```

If a match exists, skip that signal (already surfaced). Exception: if the new signal is a different `signal_type` with a higher composite score, include it with a note that the company was previously surfaced for a different reason.

---

## Error Handling

- **Web search returns no results for a signal type**: Skip that type, note in output. Don't fail the scan.
- **Supabase unavailable for dedup**: Proceed without dedup, flag `dedup_method: "skipped_supabase_unavailable"` in output.
- **Targeted scan finds no signals**: Return empty signals array with `reasoning: "No cross-border signals found for {company_name} in public sources."` This is a valid result, not an error.

---

## Reference Files

- [references/signal-types.md](references/signal-types.md) -- Signal categories, evidence patterns, and search templates
- [references/web-search-patterns.md](references/web-search-patterns.md) -- Optimized web search queries per signal type
- [references/parallel-webhook-format.md](references/parallel-webhook-format.md) -- Parallel webhook payload parsing
- [references/example-output.json](references/example-output.json) -- Example scanner output
