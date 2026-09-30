#!/bin/bash
# Build one bench page. usage: bench/run_one.sh <plain|skill> <n>
# Both arms: same brief, same model, every other skill disabled. The skill arm gets the
# tastegate folder in the project and one extra line telling it to follow SKILL.md.
arm=$1; n=$2
here=$(cd "$(dirname "$0")" && pwd); repo=$(dirname "$here")
d=${BENCH_ROOT:-/tmp/tg-bench}/$arm-$n; rm -rf "$d"; mkdir -p "$d"; cd "$d"
prompt="$(cat "$here/brief.txt")"
if [ "$arm" = skill ]; then
  mkdir -p .claude/skills; cp -r "$repo/tastegate" .claude/skills/tastegate
  prompt="$prompt

Use the tastegate skill for this: read .claude/skills/tastegate/SKILL.md and follow it."
fi
start=$(date +%s)
timeout 1800 claude -p "$prompt" --model claude-opus-5-5 --disable-slash-commands --dangerously-skip-permissions --output-format json > claude.json 2> claude.err
echo "{\"arm\":\"$arm\",\"n\":$n,\"exit\":$?,\"seconds\":$(( $(date +%s)-start ))}" > meta.json
