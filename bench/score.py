#!/usr/bin/env python3
"""Score every bench build: impeccable's own detector (the skill never runs it) + the tastegate gate."""
import collections, json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tastegate" / "scripts"))
import gate

ROOT = Path(os.environ.get("BENCH_ROOT", "/tmp/tg-bench")); OUT = Path(__file__).parent
IMP = os.environ.get("IMPECCABLE", str(Path.home() / ".claude/skills/impeccable/scripts/impeccable"))
runs = []
for d in sorted(ROOT.iterdir()):
    meta = json.loads((d / "meta.json").read_text()) if (d / "meta.json").exists() else {}
    page = d / "index.html"
    row = {"run": d.name, "arm": d.name.split("-")[0], "seconds": meta.get("seconds"), "built": page.exists()}
    try:
        cj = json.loads((d / "claude.json").read_text())
        row.update(cost_usd=cj.get("total_cost_usd"), turns=cj.get("num_turns"), is_error=cj.get("is_error"))
    except Exception:
        pass
    if page.exists():
        imp = json.loads(subprocess.run([IMP, "detect", "--json", "--no-config", str(page)], capture_output=True, text=True).stdout or "[]")
        row["impeccable_findings"] = len(imp)
        row["impeccable_rules"] = dict(collections.Counter(i.get("antipattern") for i in imp))
        rep = gate.run(str(page), OUT / "shots" / d.name, wait_ms=900)
        row["gate_fail"] = rep["fail"]; row["gate_rules"] = dict(collections.Counter(f["rule"] for f in rep["findings"] if f["severity"] == "fail"))
    runs.append(row)
summary = {}
for arm in ("plain", "skill"):
    rs = [r for r in runs if r["arm"] == arm and r.get("built")]
    if rs:
        avg = lambda k: round(sum(r[k] or 0 for r in rs) / len(rs), 1)
        summary[arm] = {"runs": len(rs), "impeccable_findings_avg": avg("impeccable_findings"), "gate_fail_avg": avg("gate_fail"),
                        "minutes_avg": round(avg("seconds") / 60, 1), "cost_usd_avg": round(sum(r.get("cost_usd") or 0 for r in rs) / len(rs), 2),
                        "impeccable_per_run": [r["impeccable_findings"] for r in rs], "gate_per_run": [r["gate_fail"] for r in rs]}
res = {"date": "2026-09-30", "model": "claude-opus-5-5 (Claude Code 2.1.281, -p, all other skills disabled)",
       "brief": (OUT / "brief.txt").read_text(), "judge": "impeccable detect --json --no-config (pbakaus/impeccable 4.4.0) + tastegate gate.py",
       "summary": summary, "runs": runs}
(OUT / "results.json").write_text(json.dumps(res, indent=2))
print(json.dumps(summary, indent=1))
for r in runs: print(r["run"], r.get("impeccable_findings"), r.get("gate_fail"), r.get("seconds"), r.get("cost_usd"), r.get("gate_rules"))
