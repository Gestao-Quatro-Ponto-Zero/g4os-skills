# Humanize Writing

Rewrite or create content that sounds naturally human. Removes all 18 AI writing patterns identified by Wikipedia's "Signs of AI writing" guide.

## What it does

- Takes AI-generated or stilted text and rewrites it to sound natural
- Creates new content from scratch without AI patterns
- Applies 18 specific anti-pattern rules (puffery, participial padding, AI vocabulary, etc.)

## Install

**Paste in G4 OS:**
```
Install the skill "humanize" from https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills — clone the repo, copy skills/humanize/ to my G4 OS skills directory, and confirm it's working.
```

**Or via terminal:**
```bash
curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- skills/humanize
```

## Usage

In G4 OS, just ask:

> "Humanize this text: [paste text]"

Or:

> "Write a blog post about X" (skill activates automatically when writing is involved)

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill definition with all 18 anti-pattern rules |
| `icon.svg` | Pen/edit icon |
