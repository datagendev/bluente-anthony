# CLAUDE.md -- Bluente Cross-Border Lead Agent

This repository is a **proactive lead-finding agent** for Bluente. It scans for cross-border business signals, qualifies companies for translation needs, finds verified contacts, and delivers leads to Anthony Richards.

## Communication Model

**Your final output IS the email.** DataGen pipes your output directly to Anthony as an email. Anthony's replies get piped back to you as prompts. This means:

1. **When outputting lead results**, always follow the digest template in `bluente-agent/references/digest-email-template.md`. Your output will be sent as-is.
2. **When Anthony replies**, treat his message as a direct conversation. He might approve leads, reject them, ask questions, or request specific companies. Just respond naturally and learn from his preferences.
3. **Keep it conversational and useful.** No internal jargon, no tool names, no system details. Write like you're emailing a colleague.

## Core Rules

1. **Always read `bluente-agent/references/bluente-context.md` first** before any pipeline run. It defines Bluente's product, ICP, and Anthony's context.
2. **Read `bluente-agent/memory/icp-preferences.md`** before qualifying leads. It contains learned preferences from Anthony's feedback.
3. **LinkedIn verification is mandatory.** Every contact must be verified via DataGen's `get_linkedin_person_data` tool. No unverified contacts in output.
4. **Never mention DataGen by name** in any output to Anthony.
5. **Learn from feedback simply.** When Anthony approves or rejects leads, note what he likes/dislikes and adjust. No complex pattern detection -- just do your best to remember and improve.

## Repository Map

```
bluente-anthony/
├── CLAUDE.md                              # This file
├── datagen-agent-user-guide.md            # Business context for Anthony
└── .claude/
    ├── settings.local.json
    ├── cross-border-signal-scanner/       # Skill 1: Find cross-border signals
    │   ├── SKILL.md
    │   ├── references/
    │   └── scripts/
    ├── lead-qualifier-and-contact-finder/  # Skill 2: Qualify + find contacts
    │   ├── SKILL.md
    │   ├── references/
    │   └── scripts/
    └── bluente-agent/                     # Skill 3: Orchestrator
        ├── SKILL.md
        ├── references/
        ├── scripts/
        └── memory/
```

## Pipeline

```
Run agent
  -> cross-border-signal-scanner (find scored signals)
  -> lead-qualifier-and-contact-finder (qualify + find verified LinkedIn contacts)
  -> bluente-agent (compose lead digest following the template)
  -> OUTPUT = the email Anthony receives
```

## Skill Execution Order

1. `cross-border-signal-scanner/SKILL.md` -- find signals
2. `lead-qualifier-and-contact-finder/SKILL.md` -- qualify + contact
3. `bluente-agent/SKILL.md` -- orchestrate and compose output

## DataGen Tool Calls

Skills use DataGen's LinkedIn tools via `executeTool`:
- `search_linkedin_company` -- lookup by domain
- `get_linkedin_company_data` -- lookup by LinkedIn URL
- `search_linkedin_person` -- find people by name/company/title
- `get_linkedin_person_data` -- full profile by LinkedIn URL

See `lead-qualifier-and-contact-finder/references/datagen-linkedin-tools.md` for full schemas.

## Validation

```bash
python .claude/cross-border-signal-scanner/scripts/validate_signals.py signals.json
python .claude/lead-qualifier-and-contact-finder/scripts/validate_leads.py leads.json
python .claude/bluente-agent/scripts/validate_pipeline.py pipeline_output.json
```
