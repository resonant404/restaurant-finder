#!/usr/bin/env bash
# Build and install the restaurant-finder skill.
#
# Does two things:
#   1. Installs into Claude Code at  ~/.claude/skills/<name>/
#   2. Produces an upload zip at     dist/<name>.zip   (for claude.ai)
#
# Run after cloning, and again after each `git pull` to refresh both.
#
# Env overrides:
#   CLAUDE_SKILLS_DIR=/path   change the Claude Code install root
#   SKIP_LOCAL_INSTALL=1      skip the local install
#   SKIP_ZIP=1                skip the zip build

set -euo pipefail

repo_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

if [ ! -f "$repo_dir/SKILL.md" ]; then
  echo "build.sh: SKILL.md not found in $repo_dir" >&2
  exit 1
fi

# Derive the skill name from SKILL.md frontmatter so install paths stay in sync.
skill_name=$(sed -n 's/^name:[[:space:]]*//p' "$repo_dir/SKILL.md" | head -n1 | tr -d '[:space:]')
if [ -z "$skill_name" ]; then
  echo "build.sh: could not read 'name:' from SKILL.md frontmatter" >&2
  exit 1
fi

# Stage the payload once, then reuse for both targets.
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT

rsync -a \
  --exclude='.git/' \
  --exclude='build.sh' \
  --exclude='dist/' \
  --exclude='LICENSE' \
  --exclude='README.md' \
  "$repo_dir/" "$stage/$skill_name/"

if [ -z "${SKIP_LOCAL_INSTALL:-}" ]; then
  skills_root="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
  dest="$skills_root/$skill_name"
  mkdir -p "$skills_root"
  # Wipe the old install so files removed upstream don't linger.
  rm -rf "$dest"
  cp -a "$stage/$skill_name" "$dest"
  echo "Installed locally:  $dest"
fi

if [ -z "${SKIP_ZIP:-}" ]; then
  dist="$repo_dir/dist"
  mkdir -p "$dist"
  zip_path="$dist/$skill_name.zip"
  rm -f "$zip_path"
  # Archive contains <name>/SKILL.md at the top, which is what claude.ai
  # expects on upload. Using python so there's no `zip` binary dependency.
  python3 -c "import shutil; shutil.make_archive('$dist/$skill_name', 'zip', '$stage', '$skill_name')"
  echo "Wrote upload zip:   $zip_path"
fi
