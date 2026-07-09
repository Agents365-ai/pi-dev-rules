#!/usr/bin/env bash
# Refresh the package catalog CSV and save a changelog snapshot.
#
# Intended cadence: weekly (Sundays) — the npm registry changes daily and Pi
# releases ship every few days, but a weekly refresh keeps this reference skill
# current without churn.
#
# Usage: bash scripts/refresh.sh
set -euo pipefail; cd "$(dirname "$0")/.."

echo "=== [1/2] Package gallery ==="
python3 scripts/fetch-pi-packages.py
echo ""

echo "=== [2/2] Changelog ==="
echo "Fetching https://pi.dev/news ..."
echo "Review the latest entries and update references/changelog.md by hand"
echo "(the news page structure varies; a human or agent judgment is best for extracting highlights)."
echo ""
echo "Done. Review git diff, then commit on a feature branch:"
echo "  git checkout -b weekly-refresh-\$(date +%Y-%m-%d)"
echo "  git add references/pi-packages.csv references/changelog.md"
echo "  git commit -m 'Weekly refresh: packages + changelog (\$(date +%Y-%m-%d))'"
echo "  git push -u origin HEAD && gh pr create --title 'Weekly refresh: packages + changelog (\$(date +%Y-%m-%d))' --body 'Automated weekly refresh.'"
