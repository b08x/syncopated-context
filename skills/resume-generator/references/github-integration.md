# GitHub Integration Reference

Optional integration with GitHub via MCP server to enrich the resume's Projects and Skills
sections with real repository data.

## Overview

When a GitHub MCP server is available in the conversation, this integration can:
- Pull repository metadata (name, description, language, stars, topics)
- Extract technology stacks from repo languages and dependency files
- Identify the user's most significant projects by activity and stars
- Supplement the Skills section with verified technologies from actual code

## MCP Server Detection

To use GitHub integration, a GitHub-compatible MCP server must be available. Common
MCP server names and endpoints include:

- `github` / `github-mcp` — Official GitHub MCP server
- Hugging Face MCP servers with GitHub access

Check the conversation's available MCP tools. If a GitHub tool is available, offer
the enrichment workflow to the user.

## Enrichment Workflow

### Step 1: Identify the User's GitHub Profile

Ask the user for their GitHub username, or infer from:
- Context in the conversation
- LinkedIn/portfolio URLs already provided
- Memory of prior conversations

### Step 2: Fetch Repository Data

Using the MCP server, retrieve the user's public repositories. Focus on:

```
For each repository, collect:
- name: Repository name
- description: One-line description
- language: Primary language
- languages: All languages used (with byte counts)
- topics: Repository topics/tags
- stargazers_count: Stars as a popularity signal
- fork: Whether it's a fork (deprioritize forks)
- pushed_at: Last push date (recency signal)
- homepage: Deployed URL if available
```

### Step 3: Filter and Rank Projects

Apply these filters:
1. Exclude forks unless the user specifically contributed significantly
2. Exclude trivially small repos (e.g., dotfiles, config-only repos) unless relevant
3. Exclude archived repos unless they are notable

Rank remaining repos by:
1. **Relevance** to the user's target role (if job-tailoring, weight toward matching technologies)
2. **Recency** — more recent active projects ranked higher
3. **Significance** — stars, description quality, topic tags

Select the top 3-6 projects (adjustable based on resume space).

### Step 4: Generate Project Entries

For each selected project, create a resume entry:

```
### {{Project Name}}
{{Description — use repo description, enhanced with context from README if available}}
- Built with {{primary language}} {{and frameworks from topics/dependencies}}
- {{Key feature or accomplishment from description/README}}
- {{Link to live demo if homepage exists}}
```

**Rules:**
- Use the repo's own description as the primary source
- Do NOT fabricate features or accomplishments not evidenced in the repo
- If the description is sparse, note this and ask the user to provide context
- Include links only to live deployments, not to the repo itself (unless requested)

### Step 5: Enrich Skills Section

From the aggregated repository data, extract:
- **Languages:** All programming languages used across repos, weighted by byte count
- **Frameworks/Tools:** From topics, dependency files, and README badges
- **Platforms:** From deployment targets (e.g., Docker, AWS, Heroku in topics)

Merge these with the user's manually provided skills:
- If a skill appears in both GitHub data and user input, keep the user's version
- GitHub-derived skills supplement but do not override user-provided skills
- Group GitHub-derived skills naturally into the existing skill categories

## Fallback Behavior

If the MCP server is unavailable or the request fails:
1. Do not error or block resume generation
2. Inform the user that GitHub enrichment is unavailable
3. Continue with manually provided project information
4. Suggest the user can add project details manually

If the user declines GitHub integration:
1. Skip the entire workflow
2. Do not mention it again in the current session unless the user asks

## Privacy Considerations

- Only access public repository data
- Do not include private repository information even if accessible
- Let the user review and approve all GitHub-derived content before including it
- Do not include contribution graphs, commit counts, or detailed activity metrics
  that might reveal work patterns
