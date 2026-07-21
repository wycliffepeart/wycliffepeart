You are maintaining a GitHub repository containing professional LinkedIn content.

Your objective is to generate ONE new LinkedIn post and update the repository.

====================================================================
Repository Structure
====================================================================

Index:
app/blog/linkedin/posts.json

Markdown root:
app/blog/linkedin/posts/

====================================================================
Existing Content
====================================================================

Before generating anything:

1. Read app/blog/linkedin/posts.json.
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

app/blog/linkedin/posts/YYYY/MM/YYYY-MM-DD-HHMMSS-<slug>.md

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

Append ONE object to app/blog/linkedin/posts.json:

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
  "markdown":"app/blog/linkedin/posts/YYYY/MM/file.md"
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
Commit Rules
====================================================================

Only after a social post has been created and validated, and only when explicitly asked to do a `git commit` or complete the GitHub workflow for that generated post:

- Use GitHub CLI (`gh`) for GitHub issue, branch, push, and pull request operations.
- Check `git status --short --branch` before changing branches or staging files.
- Confirm the intended diff and avoid including unrelated local changes in the commit.
- Create a GitHub issue first with a clear title and description of the requested changes.
- Assign the issue to the current GitHub user from `gh api user --jq .login`.
- Add the appropriate label to the issue, using `bug` for fixes and `enhancement` for new features unless the change clearly needs another existing label.
- Create a new branch from the repository default branch, not from an unrelated feature branch.
- Prefix the branch with `bug/` or `feat/` and use the pattern `[bug, feat]/WPW-[issue-id]-[issue-title]`.
- Stage only the intended files and commit with a concise imperative message.
- Push the branch to `origin`.
- Create a pull request targeting the default branch, link it to the issue with `Closes #[issue-id]`, and apply the same label used on the issue.
- Link the issue to the `wycliffepeart` GitHub project.
- If `gh` lacks required scopes, refresh the token with the minimum required scopes and continue after authorization.
- If changing files under `.github/workflows/`, ensure the GitHub token has the `workflow` scope before pushing.
- If SSH push fails because of key permissions, use the authenticated `gh` HTTPS credential flow rather than changing repository content.
- Verify the final issue, pull request, branch, labels, assignment, and project link before the handoff.

====================================================================
Rules
====================================================================

Never overwrite previous content.
Never generate more than one post.
Perform the repository modifications directly.
