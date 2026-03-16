# Fallback Responses

What to output when the pipeline can't produce a full lead list. Always deliver something useful.

---

## No Signals Found

```
Anthony,

Scanned for cross-border signals today -- nothing surfaced matching our criteria.

If you want me to look at a specific company, just reply with the company name or domain.
```

## Signals Found, None Qualified

```
Anthony,

Found {N} cross-border signals, but none were a strong fit for Bluente:
- {reason_1}
- {reason_2}

If any of these look interesting, reply with the company name and I'll dig deeper.
```

## Leads With Unverified Contacts

Include in digest with note:
```
Contact: [not verified -- couldn't find a matching role on LinkedIn]
```

## Tool Failure

```
Anthony,

Hit a temporary issue pulling data from one of my sources. Here's what I have so far:

{partial results}

Will retry next run.
```

Keep it human. Never expose tool names or error details.
