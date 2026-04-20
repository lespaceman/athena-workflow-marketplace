#!/usr/bin/env bash
set -euo pipefail

# Bump patch version for plugins that have changed files.
# Usage:
#   ./scripts/bump-versions.sh              # auto-detect changed plugins vs HEAD~1
#   ./scripts/bump-versions.sh <plugin>     # bump a specific plugin
#   BUMP=minor ./scripts/bump-versions.sh   # bump minor instead of patch

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARKETPLACE="$REPO_ROOT/.claude-plugin/marketplace.json"
BUMP_LEVEL="${BUMP:-patch}"

bump_version() {
  local version="$1"
  local major minor patch
  IFS='.' read -r major minor patch <<< "$version"
  case "$BUMP_LEVEL" in
    major) echo "$((major + 1)).0.0" ;;
    minor) echo "$major.$((minor + 1)).0" ;;
    patch) echo "$major.$minor.$((patch + 1))" ;;
    *) echo "Unknown bump level: $BUMP_LEVEL" >&2; exit 1 ;;
  esac
}

update_plugin_version() {
  local plugin_name="$1"
  local plugin_json="$REPO_ROOT/plugins/$plugin_name/.claude-plugin/plugin.json"

  if [[ ! -f "$plugin_json" ]]; then
    echo "Warning: $plugin_json not found, skipping" >&2
    return
  fi

  local current_version
  current_version=$(python3 -c "import json; print(json.load(open('$plugin_json'))['version'])")
  local new_version
  new_version=$(bump_version "$current_version")

  # Update plugin.json
  python3 -c "
import json, sys
with open('$plugin_json', 'r') as f:
    data = json.load(f)
data['version'] = '$new_version'
with open('$plugin_json', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"

  # Update .codex-plugin/plugin.json (if it exists)
  local codex_json="$REPO_ROOT/plugins/$plugin_name/.codex-plugin/plugin.json"
  if [[ -f "$codex_json" ]]; then
    python3 -c "
import json
with open('$codex_json', 'r') as f:
    data = json.load(f)
data['version'] = '$new_version'
with open('$codex_json', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"
  fi

  # Update package.json (npm package)
  local pkg_json="$REPO_ROOT/plugins/$plugin_name/package.json"
  if [[ -f "$pkg_json" ]]; then
    python3 -c "
import json
with open('$pkg_json', 'r') as f:
    data = json.load(f)
data['version'] = '$new_version'
with open('$pkg_json', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"
  fi

  # Update marketplace.json
  python3 -c "
import json
with open('$MARKETPLACE', 'r') as f:
    data = json.load(f)
for p in data['plugins']:
    if p['name'] == '$plugin_name':
        p['version'] = '$new_version'
        break
with open('$MARKETPLACE', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"

  echo "$plugin_name: $current_version -> $new_version"
}

# If a specific plugin is given, bump just that one (pin sync still runs below)
explicit_plugin=""
if [[ $# -ge 1 ]]; then
  explicit_plugin="$1"
  update_plugin_version "$explicit_plugin"
fi

# Auto-detect changed plugins from git diff
changed_plugins=()
while IFS= read -r file; do
  if [[ "$file" =~ ^plugins/([^/]+)/ ]]; then
    plugin="${BASH_REMATCH[1]}"
    # Skip if already in list
    if [[ ! " ${changed_plugins[*]:-} " =~ " $plugin " ]]; then
      changed_plugins+=("$plugin")
    fi
  fi
done < <(git diff --name-only HEAD~1 HEAD 2>/dev/null || git diff --name-only HEAD)

bumped_plugins=()
if [[ -n "$explicit_plugin" ]]; then
  bumped_plugins+=("$explicit_plugin")
fi

if [[ -z "$explicit_plugin" ]]; then
  if [[ ${#changed_plugins[@]} -eq 0 ]]; then
    echo "No plugin changes detected"
  else
    for plugin in "${changed_plugins[@]}"; do
      update_plugin_version "$plugin"
      bumped_plugins+=("$plugin")
    done
  fi
fi

# --- Workflow plugin pin syncing ---
# When a plugin version is bumped, sync the pin in every workflow.json that
# references it. Workflows whose pins change are queued for a patch bump so
# consumers see a new workflow release.

pin_touched_workflows=()

sync_workflow_pins_for_plugin() {
  local plugin_name="$1"
  local plugin_json="$REPO_ROOT/plugins/$plugin_name/.claude-plugin/plugin.json"
  [[ -f "$plugin_json" ]] || return

  local new_version
  new_version=$(python3 -c "import json; print(json.load(open('$plugin_json'))['version'])")

  shopt -s nullglob
  for wf_json in "$REPO_ROOT"/workflows/*/workflow.json; do
    local wf_name
    wf_name=$(basename "$(dirname "$wf_json")")
    local changed
    changed=$(python3 - "$wf_json" "$plugin_name" "$new_version" <<'PY'
import json, sys
wf_path, plugin_name, new_version = sys.argv[1], sys.argv[2], sys.argv[3]
with open(wf_path) as f:
    data = json.load(f)
changed = False
for p in data.get('plugins', []):
    ref = p.get('ref', '')
    # ref format: "<plugin>@<owner>/<repo>"
    name = ref.split('@', 1)[0] if '@' in ref else ref
    if name == plugin_name and p.get('version') != new_version:
        p['version'] = new_version
        changed = True
if changed:
    with open(wf_path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
print('1' if changed else '0')
PY
)
    if [[ "$changed" == "1" ]]; then
      echo "workflow $wf_name: pin $plugin_name -> $new_version"
      if [[ ! " ${pin_touched_workflows[*]:-} " =~ " $wf_name " ]]; then
        pin_touched_workflows+=("$wf_name")
      fi
    fi
  done
  shopt -u nullglob
}

for plugin in "${bumped_plugins[@]:-}"; do
  [[ -n "$plugin" ]] || continue
  sync_workflow_pins_for_plugin "$plugin"
done

# --- Workflow version bumping ---
# Any change to a workflow definition (including pin sync above) triggers a
# patch version bump.

WF_MARKETPLACE="$REPO_ROOT/.athena-workflow/marketplace.json"

update_workflow_version() {
  local wf_name="$1"
  local wf_json="$REPO_ROOT/workflows/$wf_name/workflow.json"

  if [[ ! -f "$wf_json" ]]; then
    echo "Warning: $wf_json not found, skipping" >&2
    return
  fi

  local current_version
  current_version=$(python3 -c "import json; print(json.load(open('$wf_json')).get('version', '0.0.0'))")
  local new_version
  new_version=$(bump_version "$current_version")

  # Update workflow.json
  python3 -c "
import json
with open('$wf_json', 'r') as f:
    data = json.load(f)
data['version'] = '$new_version'
with open('$wf_json', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"

  # Update .athena-workflow/marketplace.json
  if [[ -f "$WF_MARKETPLACE" ]]; then
    python3 -c "
import json
with open('$WF_MARKETPLACE', 'r') as f:
    data = json.load(f)
for w in data.get('workflows', []):
    if w['name'] == '$wf_name':
        w['version'] = '$new_version'
        break
with open('$WF_MARKETPLACE', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"
  fi

  echo "workflow $wf_name: $current_version -> $new_version"
}

# Auto-detect changed workflows from git diff (skipped in explicit-plugin mode)
changed_workflows=()
if [[ -z "$explicit_plugin" ]]; then
  while IFS= read -r file; do
    if [[ "$file" =~ ^workflows/([^/]+)/ ]]; then
      wf="${BASH_REMATCH[1]}"
      if [[ ! " ${changed_workflows[*]:-} " =~ " $wf " ]]; then
        changed_workflows+=("$wf")
      fi
    fi
  done < <(git diff --name-only HEAD~1 HEAD 2>/dev/null || git diff --name-only HEAD)
fi

# Merge in workflows whose pins were synced above.
for wf in "${pin_touched_workflows[@]:-}"; do
  [[ -n "$wf" ]] || continue
  if [[ ! " ${changed_workflows[*]:-} " =~ " $wf " ]]; then
    changed_workflows+=("$wf")
  fi
done

if [[ ${#changed_workflows[@]} -eq 0 ]]; then
  echo "No workflow changes detected"
else
  for wf in "${changed_workflows[@]}"; do
    update_workflow_version "$wf"
  done
fi
