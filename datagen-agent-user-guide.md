---
title: "Bluente Cross-Border Lead Agent -- User Guide"
status: active
created: 2026-03-16
updated: 2026-03-16
---

# Bluente Cross-Border Lead Agent

## What This Does

This agent proactively finds companies showing cross-border business signals -- mergers, international expansion, regulatory changes, new market entry -- that indicate a need for document translation services. It qualifies each signal for Bluente fit, finds the right contact at the company, and delivers a daily digest email with numbered leads you can approve or reject with a simple reply.

## How It Works

### Daily Lead Digest

Every day (or on demand), the agent:

1. **Scans** for fresh cross-border business signals across news, press releases, and business databases
2. **Qualifies** each signal: Does this company produce documents that cross language boundaries? What's the volume? What's their current solution?
3. **Finds contacts** at qualified companies -- prioritizing Localization Managers, Legal Ops, International Ops, or whoever owns the translation workflow
4. **Verifies** each contact on LinkedIn (no unverified contacts)
5. **Emails you** a numbered digest with all qualified leads

### Replying to Action

When you receive a digest, reply with any combination of:

| Command | Example | What happens |
|---------|---------|-------------|
| Approve | `approve 1, 3` or `approve all` | Leads saved to pipeline database |
| Reject | `reject 2 -- too small` | Lead skipped, reason logged for learning |
| Deep dive | `more on 1` | Agent researches that company deeper, replies with expanded intel |
| Monitor | `watch Acme Corp` | Agent adds company to watchlist for ongoing signal monitoring |

You can combine these in a single reply: `approve 1, 3. reject 2 -- too small. more on 4.`

### Learning From Your Feedback

The agent learns from your approvals and rejections:
- If you reject 5+ leads with the same reason (e.g., "too small"), it adds a filter rule
- Signal types that drop below 20% approval get demoted in future scans
- Industries showing >80% approval get promoted

This means the leads get sharper over time without you having to update any settings.

## Trigger Modes

### 1. Daily Cron (default)
Runs automatically at a configured time. Scans for signals from the past 24 hours.

### 2. Parallel Webhook
Receives webhook payloads from Parallel (or similar signal providers). Parses the structured data and runs qualification immediately.

### 3. Target Account Request
You email the agent: `watch Globex Industries` or `scan globex.com`. The agent runs a deep scan on that specific company.

### 4. Feedback Reply
You reply to a digest email with approvals/rejections. The agent processes feedback, updates the pipeline database, and confirms.

## What Gets Stored

**Approved leads** go to a Supabase database with:
- Company name, domain, signal type, evidence
- Contact name, title, LinkedIn URL
- Qualification reason and translation use case
- Status tracking: approved -> contacted -> meeting_booked -> closed_won/closed_lost

**Feedback** is logged in an append-only audit trail for pattern detection.

## Your Stack

This agent is designed to complement your existing tools:
- **Clay**: For enrichment workflows you already have running
- **Smart Lead**: For email sequencing once leads are approved
- **HeyReach**: For LinkedIn outreach campaigns
- **HubSpot**: Your CRM (agent can be extended to push approved leads)
- **Slack**: Your CEO's signal scanner already posts here -- this agent emails you directly

## Signal Types Scanned

1. **Mergers & Acquisitions** -- Cross-border M&A means contracts, compliance docs, and internal comms across languages
2. **International Expansion** -- New offices, market entry announcements, international hiring
3. **Regulatory Compliance** -- New regulations requiring multilingual documentation
4. **Cross-Border Partnerships** -- Joint ventures, distribution agreements, licensing deals
5. **New Market Entry** -- Product launches in new geographies, localization job postings

## Getting Started

1. The agent is configured and ready to run
2. You'll receive your first digest email at the configured time
3. Reply to approve/reject leads
4. The agent gets sharper with every reply
