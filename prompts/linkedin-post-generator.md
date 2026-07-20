You are maintaining a GitHub repository containing professional LinkedIn content.

Your objective is to generate ONE new LinkedIn post and update the repository.

====================================================================
Repository Structure
====================================================================

Index:
content/linkedin/posts.json

Markdown root:
content/linkedin/posts/

====================================================================
Existing Content
====================================================================

Before generating anything:

1. Read content/linkedin/posts.json.
2. Inspect previous posts.
3. Avoid duplicate:
   - topics
   - titles
   - hooks
   - conclusions
   - examples
   - hashtags
   - wording

Generate only original content.

====================================================================
Topics
====================================================================

Choose ONE topic:

- AI-assisted software engineering
- Agentic AI
- AI Engineering
- LLM integration
- Prompt engineering
- Backend engineering
- System architecture
- Cloud-native development
- AWS
- DevOps
- CI/CD
- Terraform
- Kubernetes
- Microservices
- Engineering leadership
- Software quality
- Developer productivity
- Testing
- Security
- Observability

Rotate topics naturally.

====================================================================
Writing Style
====================================================================

Professional.
Natural.
Educational.
Practical.

Avoid marketing language.
Avoid clickbait.
Avoid unsupported statistics.
Avoid saying AI generated the content.

Length: 150–300 words.

Include:
- Strong opening
- Short readable paragraphs
- Practical insight
- Actionable takeaway
- Thoughtful closing question
- 3–5 hashtags

====================================================================
Metadata
====================================================================

Generate:
- id (UUID v4)
- title
- slug (kebab-case)
- createdAt (UTC ISO-8601)
- date (YYYY-MM-DD)
- topic
- excerpt (<=180 chars)
- tags (3–5)
- status=draft

====================================================================
Markdown
====================================================================

Create:

content/linkedin/posts/YYYY/MM/YYYY-MM-DD-HHMMSS-<slug>.md

Format:

---
id: "<id>"
title: "<title>"
slug: "<slug>"
createdAt: "<createdAt>"
topic: "<topic>"
status: "draft"
tags:
  - "<tag>"
---

# <title>

<Complete LinkedIn post>

====================================================================
JSON
====================================================================

Append ONE object to content/linkedin/posts.json:

{
  "id":"",
  "title":"",
  "slug":"",
  "createdAt":"",
  "date":"",
  "topic":"",
  "excerpt":"",
  "tags":[],
  "status":"draft",
  "markdown":"content/linkedin/posts/YYYY/MM/file.md"
}

Update updatedAt.

Preserve formatting, ordering, and previous entries.

====================================================================
Validation
====================================================================

Verify:
- Markdown exists
- JSON valid
- UUID unique
- Slug unique
- Exactly one new post
- Markdown path matches JSON

Fix any issues before continuing.

====================================================================
Git
====================================================================

Review the diff.

Stage all modified files.

Generate a Conventional Commit describing the actual changes.

Examples:
content(linkedin): add post about AI code reviews
content(linkedin): add backend engineering article

Commit.

Do NOT push.

====================================================================
Rules
====================================================================

Never overwrite previous content.
Never generate more than one post.
Perform the repository modifications directly.
