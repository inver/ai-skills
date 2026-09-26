# ai-skills

A catalog of OpenCode skills.

## Structure

```
skills/          # OpenCode skills (each skill is a folder with SKILL.md)
  frontend/
    SKILL.md
  backend-api/
    SKILL.md
README.md        # This file
```

## Usage

### Creating Skills

Add new skills to the catalog:

```bash
# Add a new skill
npx @brequet/agent-sync catalog skill add my-skill

# Or manually create a folder with SKILL.md
mkdir -p skills/my-skill
# Then create skills/my-skill/SKILL.md with frontmatter
```

### SKILL.md Format

Each skill must have a SKILL.md file with frontmatter:

```markdown
---
name: my-skill
description: A helpful skill
license: MIT
compatibility: opencode
metadata:
  tags: example, demo
---

## What I do

[Describe what this skill does]

## When to use me

[Describe when to use this skill]

## Instructions

[Add detailed instructions for AI agents]
```

### Using the Catalog

Users can add this catalog:

```bash
# Local catalog
npx @brequet/agent-sync add /path/to/this/catalog

# Git catalog (once published)
npx @brequet/agent-sync add https://github.com/your-org/your-catalog
```

No build step needed - the CLI discovers skills by scanning the skills/ directory!
