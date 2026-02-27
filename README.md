# G4 OS Skills & Workflows

Community skills and workflows for [G4 OS](https://g4os.dev) — the AI Chief of Staff platform.

Skills are single-purpose tools. Workflows are multi-phase processes with knowledge bases. Both install with one command.

---

## Catalog

### Skills

| Skill | Description | Install |
|-------|-------------|---------|
| **[Humanize Writing](skills/humanize/)** | Rewrite content to sound naturally human. Removes 18 AI writing patterns from Wikipedia's "Signs of AI writing" | `skills/humanize` |
| **[Video Combiner](skills/video-combiner/)** | Combine Hook + Body + CTA video segments into ad variations with auto-subtitles in multiple aspect ratios | `skills/video-combiner` |

### Workflows

| Workflow | Description | Install |
|----------|-------------|---------|
| **[Onde Usar IA](workflows/onde-usar-ia/)** | Diagnostico interativo de IA generativa — matriz 2x2, business case quantificado, demo ao vivo. PT-BR | `workflows/onde-usar-ia` |

---

## Install

### One-line install

Pick a skill or workflow from the catalog above and run:

```bash
curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- <path>
```

**Examples:**

```bash
# Install the humanize skill
curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- skills/humanize

# Install the onde-usar-ia workflow
curl -sL https://raw.githubusercontent.com/Gestao-Quatro-Ponto-Zero/g4os-skills/main/install.sh | bash -s -- workflows/onde-usar-ia
```

The installer detects your G4 OS workspace and copies the skill/workflow to the right location. Start a new G4 OS conversation to use it.

### Manual install

Clone the repo and copy the folder you want:

```bash
git clone https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills.git
cp -r g4os-skills/skills/humanize ~/.g4os/workspaces/<your-workspace>/skills/
```

---

## How skills work

A skill is a folder with a `SKILL.md` file:

```
my-skill/
├── SKILL.md          # Required: YAML frontmatter + instructions
├── icon.svg          # Optional: icon for the UI
├── references/       # Optional: reference documents loaded on demand
└── scripts/          # Optional: executable scripts
```

A workflow is a folder with a `WORKFLOW.md` file:

```
my-workflow/
├── WORKFLOW.md       # Required: YAML frontmatter + multi-phase instructions
└── knowledge/        # Optional: domain knowledge files
```

### SKILL.md / WORKFLOW.md format

```yaml
---
name: "Display Name"
description: "What it does and when to trigger it"
icon: "🔧"                              # optional emoji
---

# Instructions

The markdown body contains the instructions that G4 OS follows
when this skill/workflow is active.
```

G4 OS auto-discovers skills and workflows from the filesystem. No registration step needed.

---

## Contributing

1. Fork this repo
2. Create a new folder under `skills/` or `workflows/`
3. Add a `SKILL.md` or `WORKFLOW.md` with valid frontmatter
4. Add a `README.md` with description and install command
5. Submit a PR

### Guidelines

- Keep the main definition file under 500 lines. Move detailed reference material to `references/` or `knowledge/`
- No hardcoded paths — use relative paths or `$HOME`
- Include a `README.md` with the one-line install command
- Test the install script before submitting

---

## License

MIT
