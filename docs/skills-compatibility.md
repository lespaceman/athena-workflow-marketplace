# Skills Compatibility Model

This repo separates portable Agent Skills core data from runtime-specific metadata.

## Goals

- Keep `SKILL.md` compatible with the Agent Skills open standard
- Keep Claude-only behavior outside portable `SKILL.md`
- Keep Codex and plugin UI metadata outside portable `SKILL.md`

## Portable Core

Each `SKILL.md` should contain only spec-safe frontmatter:

- `name`
- `description`
- `license`
- `compatibility`
- `metadata`
- `allowed-tools`

For portability, `allowed-tools` must be a space-delimited string.

## Claude Overlay

Claude-specific metadata lives in `agents/claude.yaml`:

```yaml
frontmatter:
  argument-hint: "<arg>"
  user-invocable: true
```

Add other Claude-only keys here when needed:

- `disable-model-invocation`
- `context`
- `agent`
- `hooks`
- `paths`
- `model`
- `effort`
- `shell`

## OpenAI / Codex UI Layer

Menu and presentation metadata lives in `agents/openai.yaml`:

- `display_name`
- `short_description`
- `default_prompt`

This file is not part of the portable skill core.

## Validation

Portable validation:

```bash
scripts/validate-skills-portable.sh
```

Repo-specific validation:

```bash
scripts/validate-skills-repo.sh
```

The portable validator uses `skills-ref` when installed. The repo validator checks that Claude-only
frontmatter is not leaking back into `SKILL.md`.

## Authoring

To scaffold a new compatible skill in this repo, use:

```bash
scripts/init-compatible-skill.py my-skill --path plugins/my-plugin/skills --interface display_name="My Skill" --interface short_description="Describe the skill in the UI" --interface default_prompt="Run my skill." --argument-hint "<arg>"
```

This creates:

- `SKILL.md` as the portable skill core
- `agents/openai.yaml` for Codex/OpenAI UI metadata
- `agents/claude.yaml` for Claude-only invocation metadata

Source of truth and regeneration rules:

- Treat `SKILL.md` as the hand-authored source of truth
- `agents/claude.yaml` is generated overlay metadata and may be overwritten when regenerated
- `agents/openai.yaml` is scaffolded UI metadata and may also be replaced if scaffold or metadata-generation flows are rerun for the skill
- If you hand-edit generated metadata files, assume those edits can be lost on regeneration unless you also update the generator inputs or process

To regenerate or add a Claude overlay for an existing skill:

```bash
scripts/generate-claude-yaml.py plugins/my-plugin/skills/my-skill --frontmatter user-invocable=true --frontmatter argument-hint="<arg>"
```
