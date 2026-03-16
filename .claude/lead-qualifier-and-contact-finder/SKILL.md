---
name: lead-qualifier-and-contact-finder
description: "Qualifies cross-border signals for Bluente fit, finds and verifies the right contact at each company via LinkedIn. TRIGGERS: (1) Receives scored signals from cross-border-signal-scanner, (2) User says 'qualify these signals' or 'find contacts for these companies'. This is Skill 2 in the pipeline -- receives signals, outputs qualified leads with verified contacts."
---

# Lead Qualifier and Contact Finder

> **Turn signals into people.** A signal without a verified contact is just news. Find the person who owns the translation need, verify they exist on LinkedIn, and explain why this company needs Bluente.

## What This Does

Takes scored signals from the cross-border-signal-scanner, qualifies each company for Bluente fit (do they produce documents that cross language boundaries?), finds the best contact (who owns the translation workflow?), and verifies that contact on LinkedIn. Output is qualified leads ready for the digest email.

---

## Step 1: Read ICP Preferences

Before qualifying, load `bluente-agent/memory/icp-preferences.md` to check for:
- Learned filter rules from Anthony's feedback (e.g., "skip companies < 30 employees")
- Promoted industries (higher qualification bar for demoted ones)
- Demoted signal types
- Any specific exclusion patterns

Apply these preferences as additional qualification criteria.

---

## Step 2: Qualify Each Signal

For each signal from the scanner, assess:

### Qualification Questions

1. **Does this company produce documents that cross language boundaries?**
   - Legal contracts, compliance filings, product manuals, marketing materials
   - Look at the signal type and industry

2. **What's the likely volume?**
   - M&A = high volume (hundreds of pages)
   - International expansion = moderate (ongoing stream)
   - Partnership = moderate (contracts + marketing)
   - Regulatory = high (compliance deadlines drive urgency)

3. **What's their current solution likely to be?**
   - No localization team listed on LinkedIn = probably manual/ad-hoc
   - Small company (<200 employees) = unlikely to have TMS
   - Large company with localization team = already has tooling (disqualify unless Bluente is clearly better)

4. **Does this match Bluente's sweet spot?**
   - Complex formatted documents (PDFs with charts, tables, layouts)
   - Not just simple web content or short strings
   - Multiple languages, not just one

### Qualification Output

For each signal, produce:
- `qualified`: true/false
- `qualification_reason`: Why this company needs Bluente specifically
- `translation_use_case`: The specific documents/workflow that needs translation
- `disqualification_reason`: If not qualified, why (for learning)

Skip disqualified signals. Pass qualified ones to Step 3.

---

## Step 3: Find the Right Contact

For each qualified company, find the person who owns (or would own) the translation workflow.

### Contact Hierarchy (try in order)

1. **Localization Manager / Translation Lead** -- Direct owner
2. **Legal Operations Manager** -- Owns legal document workflows (for M&A/compliance signals)
3. **International Operations / Global Ops** -- Owns cross-border workflows
4. **Content / Marketing Operations** -- For marketing-heavy use cases
5. **COO / VP Operations** -- At smaller companies, operations lead owns this

### Search Process

1. **Search by company + title keywords** using `search_linkedin_person`:
   ```
   company_name: "{company_name}"
   current_position_title: "localization" OR "translation" OR "legal operations" OR "international operations" OR "content operations"
   ```

2. **If no results**, broaden the search:
   ```
   company_name: "{company_name}"
   current_position_title: "operations" OR "legal" OR "compliance" OR "marketing"
   ```

3. **If still no results**, try by company domain via `search_linkedin_company` first to get the company LinkedIn URL, then search for employees.

4. **Pick the best match** from results based on the contact hierarchy.

### LinkedIn Verification (MANDATORY)

Every contact MUST be verified via `get_linkedin_person_data`:
- Confirm they currently work at the company (check `positions[0].companyName`)
- Confirm their title is relevant to translation/operations
- Extract: full name, current title, LinkedIn URL

**If verification fails** (person left the company, profile not found), move to the next candidate in the hierarchy. If all candidates fail, mark the lead as `contact_verified: false` with a note.

---

## Step 4: Assess Urgency

For each qualified lead with a verified contact, assess outreach urgency:

| Urgency | Criteria | Action |
|---------|----------|--------|
| `hot` | Signal <7 days old, composite >500, clear translation need | Prioritize in digest |
| `warm` | Signal <30 days old, composite >200, likely translation need | Include in digest |
| `monitor` | Older signal or lower composite, possible translation need | Include with lower priority |

---

## Output Schema

```json
{
  "scan_id": "from scanner input",
  "qualified_leads": [
    {
      "company_name": "Meridian Health Systems",
      "company_domain": "meridianhealth.com",
      "signal_type": "international_expansion",
      "signal_evidence": "from scanner",
      "signal_composite": 576,
      "qualification_reason": "Healthcare company expanding into EU requires MDR-compliant multilingual patient documentation. Complex formatted PDFs (IFUs, SDS) are core to regulatory submission.",
      "translation_use_case": "Patient information leaflets, instructions for use, safety data sheets -- all complex formatted PDFs requiring precise multilingual translation for EU MDR compliance.",
      "contact_name": "Maria Chen",
      "contact_title": "Director of Regulatory Affairs",
      "contact_linkedin_url": "https://linkedin.com/in/maria-chen-123",
      "contact_verified": true,
      "contact_search_path": "Found via search_linkedin_person with company_name + title 'regulatory'. Verified via get_linkedin_person_data -- confirmed current role.",
      "urgency": "hot",
      "urgency_reasoning": "EU MDR compliance deadline September 2026, actively expanding into 8 EU languages."
    }
  ],
  "disqualified": [
    {
      "company_name": "TinyStartup Inc",
      "company_domain": "tinystartup.com",
      "disqualification_reason": "12 employees, no evidence of document-heavy workflows. Translation need is likely simple web content, not complex formatted documents."
    }
  ],
  "qualified_count": 3,
  "disqualified_count": 1,
  "verification_stats": {
    "contacts_searched": 4,
    "contacts_verified": 3,
    "contacts_failed_verification": 1
  }
}
```

---

## Error Handling

- **LinkedIn search returns no results for a company**: Try alternative company names, check for parent company. If still nothing, mark as `contact_verified: false` with note "No LinkedIn presence found."
- **LinkedIn API rate limited**: Wait and retry once. If still failing, proceed with remaining leads and note the failure.
- **Signal has insufficient info for qualification**: Default to qualified with lower confidence. Let Anthony decide.

---

## Reference Files

- [references/datagen-linkedin-tools.md](references/datagen-linkedin-tools.md) -- LinkedIn tool schemas and usage
- [references/bluente-icp.md](references/bluente-icp.md) -- Bluente ICP for qualification criteria
- [references/translation-need-indicators.md](references/translation-need-indicators.md) -- How to identify translation needs by industry
- [references/example-output.json](references/example-output.json) -- Example qualifier output
