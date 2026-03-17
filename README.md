# Bluente Cross-Border Lead Agent

A proactive lead-finding agent for [Bluente](https://bluente.com), a document translation platform that preserves PDF formatting across 120+ languages. The agent scans for companies showing cross-border business signals (M&A, international expansion, regulatory compliance), qualifies them for translation needs, finds verified LinkedIn contacts, and delivers a numbered lead digest for review.

## How It Works

```
1. Scan for cross-border signals (Parallel FindAll + web search)
2. Dedup against existing leads in Supabase
3. Qualify each signal for Bluente fit (complex formatted docs crossing language boundaries)
4. Find + verify contacts on LinkedIn via DataGen tools
5. Compose numbered lead digest -> delivered as email
6. Anthony approves/rejects -> agent learns and improves
```

## Pipeline

The agent chains three skills:

| Skill | What it does |
|-------|-------------|
| **cross-border-signal-scanner** | Finds companies with M&A, expansion, compliance, partnership, or market entry signals. Scores each on urgency x relevance x translation_likelihood. Max 10 new leads per scan. |
| **lead-qualifier-and-contact-finder** | Qualifies signals for Bluente fit. Finds the person who owns the translation workflow. Verifies every contact on LinkedIn. |
| **bluente-agent** | Orchestrates the pipeline, composes the numbered digest, processes feedback, updates learned preferences. |

## Digest Format

The agent outputs a numbered lead list that gets emailed directly:

```
LEAD 1: Stephenson Harwood LLP

Signal: International Expansion
Evidence: Law firm launching new Madrid office...
Source: https://...
Why they need translation: Cross-border legal docs...
Contact: Kevin Norbury, Chief Operations Officer
LinkedIn: https://www.linkedin.com/in/kevin-norbury-1863454
Urgency: [HOT]
```

Reply with `approve 1, 3` or `reject 2 -- too small` to take action.

## Feedback Loop

The agent learns from approvals and rejections:
- Approved leads get saved to Supabase
- Rejections get logged with reasons
- Preferences update over time (e.g., "skip companies under 30 employees")

## Tools Used

| Tool | Purpose |
|------|---------|
| `parallel_findall` / `WebSearch` | Signal discovery (Parallel primary, WebSearch fallback) |
| `search_linkedin_person` | Find contacts by company + title |
| `get_linkedin_person_data` | Verify contacts on LinkedIn |
| `search_linkedin_company` | Company lookup by domain |
| `bluente_check_dedup` | Batch dedup check against Supabase |
| `bluente_save_leads_batch` | Batch save approved leads to Supabase |

## Deployment

This repo is deployed on [DataGen](https://datagen.dev). The agent runs as a Claude Code agent in the cloud.

```bash
# Connect repo
datagen github connect-repo datagendev/bluente-anthony

# Deploy
datagen agents deploy <agent-id>

# Trigger a run
datagen agents run <agent-id> --payload '{"message": "find leads"}'

# Check logs
datagen agents logs <agent-id>
```

## Repo Structure

```
bluente-anthony/
├── CLAUDE.md                     # Agent navigation guide
├── README.md                     # This file
├── datagen-agent-user-guide.md   # Business context
└── .claude/
    ├── settings.local.json
    ├── agents/
    │   └── bluente-agent.md      # Agent definition (DataGen discovers this)
    ├── cross-border-signal-scanner/
    │   ├── SKILL.md
    │   ├── references/           # Signal types, search patterns, examples
    │   └── scripts/              # Validation scripts
    ├── lead-qualifier-and-contact-finder/
    │   ├── SKILL.md
    │   ├── references/           # ICP, LinkedIn tools, translation indicators
    │   └── scripts/              # Validation scripts
    └── bluente-agent/
        ├── SKILL.md
        ├── references/           # Bluente context, digest template, user.md
        ├── scripts/              # Pipeline validation, logging, dedup
        └── memory/               # ICP preferences, feedback log, session summary
```
