# agent-skills

The skills I work with every day when I build software with AI coding agents.

They are model-agnostic: each skill is a folder with a `SKILL.md` and, where needed, scripts and
templates. Any agent that reads the `SKILL.md` format can use them (Claude Code, Codex, Cursor and
others), and most are plain instructions that work in any tool that accepts a prompt file.

## My skills

| Skill | What it does |
|---|---|
| [agent-scaffold](skills/agent-scaffold) | Sets up and maintains an agent knowledge structure in a project: an `AGENTS.md` router plus an `agents/` folder with registers for decisions, lessons, sources and questions, templates, scripts and roles. Agents record what they learn as they work, and a curator role keeps it clean. Everything is copied into the project, so it keeps working without the skill. |
| [planning-handoff](skills/planning-handoff) | Turns finished planning, design or debugging into a `handoff/` plan with numbered, paste-ready unit prompts. Each unit has its branch, focused tests and commit; a final unit reviews, verifies and waits for approval before merging. |
| [cross-device-handoff](skills/cross-device-handoff) | Extension of planning-handoff for planning on one machine and building on another. |
| [t3-handoff-run](skills/t3-handoff-run) | Runs a handoff plan as T3 Code threads: one thread per unit, started as dependencies land, with status, stall detection and a kill switch. |
| [shared-tool-scaffold](skills/shared-tool-scaffold) | Scaffolds a small browser-based team tool that colleagues run from a shared SharePoint/OneDrive folder: Flask backend, single-file frontend, double-click start files, device-local virtualenv, atomic saves with backups, and live multi-user sync with conflict handling. The patterns come from lessons I learned building shared tools during my time at BCG. |
| [course-study-assistant](skills/course-study-assistant) | Template for a course-specific study assistant that answers from the lecture's own material and conventions and keeps a qualitative record of what the learner has understood. |
| [english-headsup](skills/english-headsup) | Occasionally appends a one-line tip on my English, without interrupting the task. |

## Skills by others that I use

Not copied here; please get them from their authors.

| Skill | Author | Source |
|---|---|---|
| grill-me, handoff, wait-what, improve-codebase-architecture | Matt Pocock | [mattpocock/skills](https://github.com/mattpocock/skills) |
| unslop | Cursor | [cursor/plugins](https://github.com/cursor/plugins) |
| caveman | Julius Brussee | [juliusbrussee/caveman](https://github.com/juliusbrussee/caveman) |
| brag | latent-spaces | [latent-spaces/brag](https://github.com/latent-spaces/brag) |
| arena | Marius Florescu | [mariusflorescu/pstack-t3](https://github.com/mariusflorescu/pstack-t3) |
| captain-obvious | shmulc8 | [shmulc8/captain-obvious](https://github.com/shmulc8/captain-obvious) |

## Install

Copy a skill folder into your agent's skills directory, for example:

```bash
git clone https://github.com/fabian-kir/agent-skills
cp -r agent-skills/skills/planning-handoff ~/.claude/skills/
```

For agents without a skills directory, point them at the `SKILL.md` or paste it into the prompt.
