#!/usr/bin/env bash
# Restore the pristine mirror so the build script can run again.
#
# WHY THIS EXISTS: `git checkout -- .` stops working the moment the built site
# has been committed. It restores the BUILD, and a one-way build refuses to run
# over itself. So the index is pointed at the pristine-mirror commit, the tree is
# written out from it, and anything the content pass added (renamed slug folders,
# the README) is cleaned away.
#
# docs/ and README.md are carried across untouched: both are newer than that
# commit, and a rebuild that deletes your own notes is a rebuild nobody trusts.
# The original version of this script cost two fixes by reverting docs/ silently.
#
#   bash docs/reset.sh
#
# Expects a `pristine-mirror` tag on the untouched-mirror commit. Falls back to
# the second commit in history (mirror, then assets) if the tag is missing.
set -euo pipefail
cd "$(dirname "$0")/.."

if git rev-parse -q --verify refs/tags/pristine-mirror >/dev/null; then
  BASE=$(git rev-parse refs/tags/pristine-mirror)
else
  BASE=$(git log --format=%H --reverse | sed -n 2p)
  echo "no pristine-mirror tag, falling back to $(git log -1 --format=%s "$BASE")"
fi

# docs/, README.md and clone.json are TRACKED at the pristine commit, so
# checkout-index would revert them to the mirror-day versions. They are copied
# out and back. The original script did not do this and silently reverted two
# fixes.
KEEP_COPY=(docs README.md clone.json)

# Everything else the content build needs is untracked, so the only thing that
# threatens it is `git clean`. Excluding it there is both safer and far faster
# than copying it: data/ alone is several hundred megabytes, and a copy has a
# window in which a concurrent writer's file is lost.
CLEAN_KEEP=(data scripts src build .vercel node_modules package.json package-lock.json vercel.json)

KEEP=$(mktemp -d)
for p in "${KEEP_COPY[@]}"; do
  [ -e "$p" ] && cp -R "$p" "$KEEP/" || true
done

CLEAN_ARGS=()
for p in "${CLEAN_KEEP[@]}"; do CLEAN_ARGS+=(-e "/$p"); done

git read-tree "$BASE"
git checkout-index -a -f
git clean -fdq "${CLEAN_ARGS[@]}"

for p in "${KEEP_COPY[@]}"; do
  base=$(basename "$p")
  if [ -e "$KEEP/$base" ]; then
    rm -rf "$p"
    cp -R "$KEEP/$base" "$p"
  fi
done
rm -rf "$KEEP"
git read-tree HEAD                                   # index back where it was
echo "reset to $(git log -1 --format=%s "$BASE")"
