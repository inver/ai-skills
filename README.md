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
# Create a folder with SKILL.md
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
# Install skills from the GitHub repository
npx skillfish add your-org/your-catalog

# Or install a specific skill from it
npx skillfish add your-org/your-catalog my-skill
```

No build step needed - the CLI discovers skills by scanning the skills/ directory!
