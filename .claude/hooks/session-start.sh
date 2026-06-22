#!/bin/bash
# SessionStart hook: ensure the pua@pua-skills plugin is enabled globally
# (user scope) for every Claude Code session in this environment, not just
# when working inside this repo. Idempotent and non-interactive.
set -euo pipefail

# Only meaningful in the remote (Claude Code on the web) environment, whose
# user-scope settings are ephemeral and otherwise reset on each rebuild.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

SETTINGS="${HOME}/.claude/settings.json"
mkdir -p "${HOME}/.claude"

python3 - "$SETTINGS" <<'PY'
import json, sys, os

path = sys.argv[1]
try:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        data = {}
except (FileNotFoundError, json.JSONDecodeError):
    data = {}

marketplaces = data.setdefault("extraKnownMarketplaces", {})
marketplaces.setdefault("pua-skills", {
    "source": {"source": "github", "repo": "tanweai/pua"}
})

enabled = data.setdefault("enabledPlugins", {})
enabled["pua@pua-skills"] = True

tmp = path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
os.replace(tmp, path)
print("pua@pua-skills enabled globally in", path)
PY
