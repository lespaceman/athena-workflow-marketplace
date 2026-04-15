---
name: export-pdf
description: >
  Export markdown file(s) to styled dark-theme PDF. Use when the user asks to "export to PDF", "convert markdown to PDF", "generate PDF", "make a PDF from markdown", or "export md".
allowed-tools: Bash(node:*) Read Glob
---

Export the specified markdown file(s) to a clean, dark-themed PDF.

## Instructions

1. Resolve the path(s) from `$ARGUMENTS`. If it is a glob pattern, use the Glob tool to expand it. If no argument is provided, ask the user which file to export.

2. Resolve the plugin root:
   - If `ATHENA_PLUGIN_ROOT` is set, use it.
   - In Claude Code plugin skills, start from `${CLAUDE_SKILL_DIR}` and go up two directories to reach the plugin root.
   - Otherwise derive it as the directory two levels above the current `SKILL.md` file.

3. For each markdown file, run the generation script:

```
node "<plugin-root>/scripts/generate-pdf.mjs" "<absolute-path-to-md-file>"
```

The script will:
- Auto-derive the document label from the filename (e.g., `self-correction-report.md` → "Self Correction Report")
- Output the PDF in the same directory as the source file
- Apply the dark-theme stylesheet with clean typography and spacing

4. Report the result to the user — list each PDF created and its path.

5. If the script reports an error about `puppeteer-core` not being installed, run:

```
cd "<plugin-root>" && npm install puppeteer-core
```

Then retry the export.
