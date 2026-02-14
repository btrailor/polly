#!/usr/bin/env bash
# Install internal Polly libraries in editable mode.
# Run from the project root: ./scripts/install_libs.sh
# Or: bash scripts/install_libs.sh

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f requirements.txt ]]; then
  echo "Run this script from the Polly project root (where requirements.txt is)." >&2
  exit 1
fi

echo "Installing Polly internal libraries (editable) from $ROOT/libs/ ..."
for dir in libs/polly-routing libs/polly-patterns libs/polly-compression libs/polly-entities libs/polly-personas; do
  if [[ -d "$dir" ]] && [[ -f "$dir/pyproject.toml" ]]; then
    echo "  - $dir"
    pip install -e "$dir"
  fi
done
echo "Done. App dependencies: pip install -r requirements.txt (from project root)."
