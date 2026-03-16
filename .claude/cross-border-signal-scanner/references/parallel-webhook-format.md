# Parallel Webhook Format

When the agent receives a webhook from Parallel (or similar signal provider), parse the payload into the signal scanner's schema.

---

## Expected Payload Structure

Parallel sends structured JSON payloads via webhook. The exact format depends on the configured signal types, but the general structure is:

```json
{
  "event_type": "signal_detected",
  "timestamp": "2026-03-16T10:30:00Z",
  "signal": {
    "company": {
      "name": "Globex Industries",
      "domain": "globex.com",
      "linkedin_url": "https://linkedin.com/company/globex",
      "employee_count": 850,
      "industry": "Manufacturing"
    },
    "type": "acquisition | expansion | partnership | funding | hiring",
    "title": "Globex Industries Acquires Tokyo-Based Yamada Corp",
    "summary": "Globex Industries announced the acquisition of Yamada Corp...",
    "source_url": "https://example.com/article",
    "published_date": "2026-03-15",
    "confidence": 0.92,
    "metadata": {
      "countries": ["US", "JP"],
      "languages": ["English", "Japanese"],
      "deal_value": "$450M",
      "keywords": ["acquisition", "manufacturing", "japan", "expansion"]
    }
  }
}
```

---

## Mapping to Signal Schema

| Parallel field | Scanner field | Notes |
|---------------|--------------|-------|
| `signal.company.name` | `company_name` | Direct |
| `signal.company.domain` | `company_domain` | Direct |
| `signal.type` | `signal_type` | Map: `acquisition` -> `merger_acquisition`, `expansion` -> `international_expansion`, `partnership` -> `cross_border_partnership`, `hiring` -> `new_market_entry` |
| `signal.summary` | `signal_evidence` | Direct |
| `signal.source_url` | `source_url` | Direct |
| `signal.confidence` | Scoring input | Use as baseline for relevance score (0.9+ -> 8-10, 0.7-0.9 -> 5-7, <0.7 -> 3-5) |
| `signal.metadata.countries` | `detected_languages` | Look up primary languages for listed countries |
| `signal.metadata.keywords` | Scoring input | Check for translation-relevant keywords |

---

## Scoring Adjustments for Webhook Signals

Webhook signals come pre-filtered, so they generally score higher:
- Start urgency at 6+ (Parallel already filtered for recency)
- Use `confidence` to adjust relevance score
- Still independently assess `translation_likelihood` based on industry, company size, and signal type

---

## Handling Multiple Signals in One Payload

Some webhooks batch multiple signals:

```json
{
  "event_type": "batch_signals",
  "signals": [ ... ]
}
```

Process each signal independently. Dedup within the batch before checking Supabase.
