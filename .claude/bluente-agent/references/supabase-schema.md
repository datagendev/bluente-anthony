# Supabase Schema

## Table: `bluente_leads`

```sql
CREATE TABLE bluente_leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_name TEXT NOT NULL,
  company_domain TEXT NOT NULL,
  signal_type TEXT NOT NULL,
  signal_evidence TEXT NOT NULL,
  qualification_reason TEXT NOT NULL,
  translation_use_case TEXT,
  contact_name TEXT NOT NULL,
  contact_title TEXT,
  contact_linkedin_url TEXT,
  urgency TEXT,
  source_scan_id TEXT NOT NULL,
  approved_at TIMESTAMPTZ DEFAULT NOW(),
  status TEXT DEFAULT 'approved',
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT unique_company_contact UNIQUE (company_domain, contact_linkedin_url)
);
```

### Status Values

| Status | Meaning |
|--------|---------|
| `approved` | Anthony approved, not yet contacted |
| `contacted` | Outreach sent |
| `meeting_booked` | Meeting scheduled |
| `closed_won` | Deal closed |
| `closed_lost` | Deal lost |

### Dedup

On conflict, append new signal info to notes:

```sql
INSERT INTO bluente_leads (...) VALUES (...)
ON CONFLICT (company_domain, contact_linkedin_url)
DO UPDATE SET
  notes = CONCAT(bluente_leads.notes, E'\n---\n', 'New signal: ', EXCLUDED.signal_type, ' -- ', EXCLUDED.signal_evidence),
  signal_type = EXCLUDED.signal_type,
  signal_evidence = EXCLUDED.signal_evidence;
```
