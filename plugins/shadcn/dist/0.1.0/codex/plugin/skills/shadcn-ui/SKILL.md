---
name: shadcn-ui
description: >
  MUST load BEFORE adding, composing, theming, or installing shadcn/ui components, and BEFORE any mcp__plugin_shadcn_shadcn__* tool call. Trigger on ANY of: "shadcn", "shadcn/ui", "components.json", "@shadcn", "@acme", "@tailark", "registry", "namespaced registry", "private registry", "add a button/dialog/card/form/sheet/sidebar", "build a login form", "build a dashboard", "build a settings page", "landing page with shadcn", "switch preset", "--preset", "OKLCH", "CSS variables theming", "dark mode tokens", "shadcn init/add/search/view/docs/diff/info/build", "registry.json", "publish a registry", "FieldGroup", "ToggleGroup", "radix base". Without this skill, output uses wrong base APIs, invents component names, skips registry resolution, ignores the project's aliases and icon library, and misuses theming tokens.
allowed-tools: mcp__plugin_shadcn_shadcn__get_project_registries mcp__plugin_shadcn_shadcn__list_items_in_registries mcp__plugin_shadcn_shadcn__search_items_in_registries mcp__plugin_shadcn_shadcn__view_items_in_registries mcp__plugin_shadcn_shadcn__get_item_examples_from_registries mcp__plugin_shadcn_shadcn__get_add_command_for_items mcp__plugin_shadcn_shadcn__get_audit_checklist Bash Read Write Edit Glob Grep
---

# shadcn/ui

Use this skill to install, compose, theme, and customize shadcn/ui components in a real project, and to author or consume custom registries through the shadcn MCP server.

## Input

Parse the user's intent from: $ARGUMENTS

Typical intents:
- Add specific components (`button`, `dialog`, `form`, `sidebar`, …)
- Build a feature using shadcn (login form, settings page, dashboard, landing page)
- Add components from a namespaced registry (`@acme/hero`, `@tailark/...`)
- Theme adjustments (preset switch, dark mode, OKLCH colors, radius)
- Author or publish a registry (`registry.json`, `shadcn build`)
- Fix MCP wiring or troubleshoot registry access

## Workflow

1. **Detect the project.** Confirm a `components.json` exists at the project root. If missing, the project is not shadcn-initialized — offer to run `npx shadcn@latest init` (do not run without confirmation; it edits Tailwind config and global CSS).

2. **Load project context first, every time.** Before generating component code, read project state:
   - Run `npx shadcn@latest info --json` (or call `mcp__plugin_shadcn_shadcn__get_project_registries` for the registry slice).
   - Capture: framework, Tailwind version, aliases, base library (`radix` vs `base`), icon library, installed components, configured registries.
   - When the MCP server is connected, prefer its tools over shelling out to the CLI for browsing/searching — it is faster and structured.

3. **Discover before writing code.** Never invent component names or APIs.
   - List/search via `mcp__plugin_shadcn_shadcn__list_items_in_registries` or `search_items_in_registries`.
   - View shape via `view_items_in_registries`.
   - Pull working snippets via `get_item_examples_from_registries`.
   - For long-form docs the MCP does not expose, fall back to `npx shadcn@latest docs <component>`.

4. **Install the right way.** Resolve the install command via `get_add_command_for_items` (it respects the project's package manager and registries), then run it. Examples:
   - `npx shadcn@latest add button dialog card`
   - `npx shadcn@latest add @acme/hero @acme/features`
   - Use `--yes` only when the user has confirmed overwrites.
   - Prefer `--dry-run` first when overwriting existing files.

5. **Compose using shadcn rules.**
   - Forms: use the new `Field` primitives — `Field`, `FieldGroup`, `FieldLabel`, `FieldDescription`, `FieldError` — and integrate with `react-hook-form` + `zod` when the project already uses them.
   - Option sets: prefer `ToggleGroup` over rolled-your-own button groups.
   - Use semantic color tokens (`bg-background`, `text-foreground`, `border`, `muted`, `accent`, `destructive`, `ring`) — never raw Tailwind palette colors for UI chrome.
   - Respect the configured base: `radix` vs `base` change the underlying primitives and prop surface — do not mix.
   - Honor the project's icon library (`lucide-react`, `@radix-ui/react-icons`, etc.) discovered via `info`.
   - Honor aliases from `components.json` (`@/components/ui/...`, `@/lib/utils`, etc.) — never hardcode `src/...`.

6. **Theming.**
   - Tokens live as CSS variables in the project's globals stylesheet; values are OKLCH.
   - Tailwind v4 projects use the `@theme` block; v3 projects use `tailwind.config.{ts,js}`. Detect from `info`.
   - Dark mode is class-driven (`.dark { ... }`); add overrides only inside the dark block.
   - For preset switches (`--preset`), use `npx shadcn@latest add --preset <code>` and let it rewrite tokens.
   - Border radius is a single token (`--radius`) cascaded by `rounded-lg/md/sm` utilities — change once, not per-component.

7. **Registry authoring** (when the user wants to publish/share components).
   - `registry.json` declares `name`, `homepage`, and an `items[]` array. Each item: `name`, `type` (`registry:ui` | `registry:block` | `registry:hook` | `registry:lib` | `registry:theme` | `registry:style`), `files[]` (each with `path`, `type`, optional `target`), `dependencies[]`, `devDependencies[]`, `registryDependencies[]`, optional `cssVars` and `tailwind`.
   - Build with `npx shadcn@latest build` → emits `public/r/<item>.json`.
   - Host the JSON anywhere static; users add it to `components.json` under `registries` as `"@ns": "https://host/r/{name}.json"` (or an object with `headers` for private registries).
   - Private registries pull tokens from `.env.local` via `${VAR}` substitution in headers.

8. **MCP setup help.** If the user asks to wire shadcn MCP into a client:
   - Claude Code: `npx shadcn@latest mcp init --client claude` writes `.mcp.json`. (This plugin already provides the same `.mcp.json` config — do not duplicate if installed via this plugin.)
   - Cursor: `npx shadcn@latest mcp init --client cursor` writes `.cursor/mcp.json`; user then enables it in settings.
   - VS Code: `npx shadcn@latest mcp init --client vscode` writes `.vscode/mcp.json`; user clicks Start.
   - Codex: run `npx shadcn@latest mcp init --client codex`, then manually append to `~/.codex/config.toml`:
     ```toml
     [mcp_servers.shadcn]
     command = "npx"
     args = ["shadcn@latest", "mcp"]
     ```
   - OpenCode: `npx shadcn@latest mcp init --client opencode` then restart.

9. **Verify.** After installation:
   - Confirm new files landed under the configured `aliases.ui` path.
   - Run `npx shadcn@latest diff` if updating existing components.
   - Use `mcp__plugin_shadcn_shadcn__get_audit_checklist` to surface follow-ups (deps to install, tokens to wire, providers to mount).

## Output Format

Always include:
1. **What you did** — components added, files written, configs touched.
2. **Source of truth** — registry/namespace each item came from, exact version or commit if pinned.
3. **Composition notes** — primitives used, base-specific APIs, semantic tokens applied.
4. **Follow-ups** — items from the audit checklist (peer deps, providers, env vars, dark-mode wiring).
5. **Selectors / aliases** — the import paths the user should use (`@/components/ui/...`).

## Operating Heuristics

- Never hand-write a component that exists in the registry — install it.
- Never use `bg-blue-500` style raw colors in UI chrome — use semantic tokens.
- Never assume the base is `radix`; check `info` first.
- Never edit files inside `components/ui/*` lightly — they are owned by shadcn and will be overwritten on update unless the user accepts the divergence (use `diff` to track).
- Never set per-component CSS variables when a global token would do.
- Never invent a registry namespace — only use namespaces present in `components.json`.
- Treat `components.json` as ground truth; if a value seems off, ask the user before mutating it.
- For private registries, never log or echo the resolved Authorization header — only confirm presence of the env var.
- When the MCP returns multiple matches, show the user the top results with name, registry, and one-line description before installing.

## Do / Don't

Do:
- Run `info` before generating code.
- Use `Field*` and `ToggleGroup` patterns.
- Pin registry items by name + namespace.
- Keep theming changes in tokens, not per-element.

Don't:
- Run `init` silently — it rewrites globals and Tailwind config.
- Fabricate component or registry names.
- Mix `radix` and `base` APIs.
- Hardcode colors that have a semantic token.
- Commit `.env.local` or registry tokens.
