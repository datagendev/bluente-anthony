# DataGen LinkedIn Tools Reference

These are DataGen default tools (NOT custom tools). Call them via `DataGen:executeTool` with `tool_alias_name`.

---

## Person Tools

### `search_linkedin_person`

Search for LinkedIn profiles by name, company, title, location, or other filters.

**Call pattern:**
```
DataGen:executeTool
  tool_alias_name: "search_linkedin_person"
  parameters: { ... }
```

**Parameters (all optional, but provide at least one):**

| Parameter | Type | Description |
|-----------|------|-------------|
| `first_name` | str | First name (starts-with matching) |
| `last_name` | str | Last name (starts-with matching) |
| `company_name` | str | Current company name (starts-with matching) |
| `headline` | str | Profile headline (contains matching) |
| `current_position_title` | str | Current job title (contains matching) |
| `location_city` | str | City (starts-with matching) |
| `location_country_code` | str | Country codes, comma-separated (e.g., "US,GB,DE") |
| `current_company_id` | str | LinkedIn company slug or numeric ID |
| `company_industries` | str | Comma-separated industries |
| `current_company_employee_count_min` | int | Minimum company employee count |
| `current_company_employee_count_max` | int | Maximum company employee count |
| `page` | int | Page number (default 1, 20 results/page) |

**Response:**
```json
{
  "persons": [
    {
      "publicIdentifier": "john-doe-123",
      "linkedInUrl": "https://linkedin.com/in/john-doe-123",
      "firstName": "John",
      "lastName": "Doe",
      "headline": "VP Revenue Operations at Acme",
      "currentPositionTitle": "VP Revenue Operations",
      "currentCompanyName": "Acme Corp",
      "updateDate": "2025-12-01"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 3,
    "totalResults": 47,
    "resultsPerPage": 20
  },
  "person": { ... }
}
```

**Tips:**
- `company_name` uses starts-with matching. "Acme" matches "Acme Corp" and "Acme Inc."
- Combine `first_name` + `last_name` + `company_name` for best precision when finding a known person.
- Use `current_position_title` for broader role-based searches (e.g., "localization" or "legal operations").

---

### `get_linkedin_person_data`

Get full LinkedIn profile data including work history, education, and skills.

**Call pattern:**
```
DataGen:executeTool
  tool_alias_name: "get_linkedin_person_data"
  parameters: { "linkedin_url": "https://linkedin.com/in/john-doe" }
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `linkedin_url` | str | Yes | Full LinkedIn profile URL |

**Response:**
```json
{
  "person": {
    "firstName": "John",
    "lastName": "Doe",
    "headline": "VP Revenue Operations at Acme",
    "location": "San Francisco, California",
    "summary": "I help SaaS companies build scalable revenue engines...",
    "linkedInUrl": "https://linkedin.com/in/john-doe",
    "photoUrl": "https://...",
    "followerCount": 2450,
    "openToWork": false,
    "positions": {
      "positionsCount": 5,
      "positionHistory": [
        {
          "title": "VP Revenue Operations",
          "companyName": "Acme Corp",
          "description": "Leading RevOps for a 200-person SaaS company...",
          "startEndDate": {
            "start": { "month": 3, "year": 2023 },
            "end": null
          }
        }
      ]
    },
    "schools": {
      "educationsCount": 1,
      "educationHistory": [
        {
          "schoolName": "University of Michigan",
          "degreeName": "BS",
          "fieldOfStudy": "Business Administration",
          "startEndDate": { ... }
        }
      ]
    },
    "skills": ["Salesforce", "HubSpot", "Revenue Operations", "Data Analysis"],
    "languages": ["English", "Spanish"]
  }
}
```

**Key fields for contact verification:**
- `positions[0].companyName` -- verify they currently work at the target company
- `positions[0].title` -- verify role relevance
- `headline` -- quick title check
- `linkedInUrl` -- canonical URL for the lead record

---

### `get_linkedin_person_posts`

Get recent posts from a LinkedIn profile including content and engagement.

**Call pattern:**
```
DataGen:executeTool
  tool_alias_name: "get_linkedin_person_posts"
  parameters: { "linkedin_url": "https://linkedin.com/in/john-doe" }
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `linkedin_url` | str | Yes | Full LinkedIn profile URL |

**Response:**
```json
{
  "posts": [
    {
      "activityId": "urn:li:activity:123456",
      "text": "Just spent 3 hours manually translating our product docs...",
      "reactionsCount": 45,
      "commentsCount": 12,
      "activityDate": "2025-11-28",
      "activityUrl": "https://linkedin.com/feed/update/..."
    }
  ]
}
```

**Optional for this pipeline** -- use only if you want additional context about a contact's pain points.

---

## Company Tools

### `search_linkedin_company`

Search for a LinkedIn company profile by domain.

**Call pattern:**
```
DataGen:executeTool
  tool_alias_name: "search_linkedin_company"
  parameters: { "domain": "acme.com" }
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `domain` | str | Yes | Company domain (e.g., "acme.com") |

**Response:**
```json
{
  "company": {
    "linkedInId": "12345678",
    "name": "Acme Corp",
    "universalName": "acme-corp",
    "linkedInUrl": "https://linkedin.com/company/acme-corp",
    "employeeCount": 187,
    "employeeCountRange": { "start": 51, "end": 200 },
    "websiteUrl": "https://acme.com",
    "tagline": "Revenue operations for modern SaaS",
    "description": "Acme Corp helps SaaS companies...",
    "industry": "Computer Software",
    "specialities": ["RevOps", "Sales Automation"],
    "followerCount": 3200,
    "headquarter": {
      "city": "San Francisco",
      "country": "US",
      "geographicArea": "California"
    }
  }
}
```

**Key fields for qualification:**
- `employeeCount` -- size check against ICP
- `industry` -- industry fit scoring
- `description` -- understand what the company does
- `headquarter.country` -- cross-border context

---

### `get_linkedin_company_data`

Get full company profile by LinkedIn URL (use when domain lookup fails).

**Call pattern:**
```
DataGen:executeTool
  tool_alias_name: "get_linkedin_company_data"
  parameters: { "linkedin_url": "https://linkedin.com/company/acme-corp" }
```

Same response schema as `search_linkedin_company`.

---

## Size Estimation Guide

Map `employeeCount` to ICP fit:

| Employee Count | Size Category | Bluente Fit |
|----------------|---------------|-------------|
| 1-19 | Micro | Poor -- low volume |
| 20-49 | Small | Possible if document-heavy |
| 50-200 | SMB | Good -- sweet spot |
| 201-1000 | Mid-market | Excellent -- sweet spot |
| 1001-5000 | Upper mid-market | Good -- may have some localization tooling |
| 5000+ | Enterprise | Risky -- likely has TMS already |
