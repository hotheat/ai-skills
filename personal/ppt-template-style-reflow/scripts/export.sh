#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CODEX_NODE_MODULES="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"
if [[ -d "$CODEX_NODE_MODULES" ]]; then
  export NODE_PATH="$CODEX_NODE_MODULES${NODE_PATH:+:$NODE_PATH}"
fi

exec "${NODE:-node}" "$SCRIPT_DIR/export_pptd_to_pptx.cjs" "$@"
