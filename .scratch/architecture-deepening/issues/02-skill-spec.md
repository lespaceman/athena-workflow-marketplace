---
title: Introduce SkillSpec for the SKILL.md ↔ claude.yaml ↔ openai.yaml triple
labels: [ready-for-human, architecture]
depends_on: []
---

# Introduce `SkillSpec` for the SKILL.md ↔ claude.yaml ↔ openai.yaml triple

## Context

Skills use a three-file model: portable `SKILL.md`, regenerable `agents/claude.yaml`, regenerable `agents/openai.yaml`. The mapping rule between these files lives in **two** places:

- `scripts/generate-claude-yaml.py` lines 14–25 — `ALLOWED_KEYS` set (Claude-only frontmatter keys).
- `scripts/validate-skills-repo.sh` lines 21–32 — `portable_forbidden` set (the inverse: keys that must NOT appear in SKILL.md).

These two lists must stay synchronized but live in separate files in different languages. CLAUDE.md (lines 38–40) is a third location documenting the split.

## Deepening

Introduce a `SkillSpec` module under `scripts/skill_model/` (Python).

### Interface

- `SkillSpec.load(path) -> SkillSpec` — reads SKILL.md frontmatter, `agents/claude.yaml`, `agents/openai.yaml`.
- `spec.portable_frontmatter` — the SKILL.md frontmatter dict.
- `spec.claude_overlay()` — projection to claude.yaml content.
- `spec.validate()` — checks portable frontmatter contains only allowed keys; claude.yaml contains only Claude-specific keys; openai.yaml carries the three required interface fields (`display_name`, `short_description`, `default_prompt`).

### Two adapters at the seam

- **Claude** — in-tree, generation owned (replaces `generate-claude-yaml.py`).
- **OpenAI** — out-of-tree, generation delegated to upstream Codex `init_skill.py`. We **validate** the resulting `openai.yaml` rather than generate it.

This satisfies the "two adapters = real seam" rule. The OpenAI adapter being externally owned is fine; it's still a real adapter.

### Behind the seam

- The single allowed-keys table (replaces ALLOWED_KEYS + portable_forbidden duplication).
- The "claude.yaml is generated" rule.
- Per-skill validation that today is split across `validate-skills-portable.sh` and `validate-skills-repo.sh`.

### Composition with #01

`MarketplaceModel.plugin(name).skills() -> list[SkillSpec]`. The two modules compose; `SkillSpec` is independently shippable.

### Deletion test

Delete the module → ALLOWED_KEYS and portable_forbidden diverge again; `init-compatible-skill.py` regrows the manual call sequence to `generate-claude-yaml.py`; validators regrow the inverse-list. Earns its keep.

## Out of scope

- Replacing the upstream Codex init tool. We continue to delegate OpenAI overlay generation; we just validate the result.
