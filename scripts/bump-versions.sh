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

# If a specific plugin is given, bump just that one
if [[ $# -ge 1 ]]; then
  update_plugin_version "$1"
  exit 0
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

if [[ ${#changed_plugins[@]} -eq 0 ]]; then
  echo "No plugin changes detected, nothing to bump"
  exit 0
fi

for plugin in "${changed_plugins[@]}"; do
  update_plugin_version "$plugin"
done
