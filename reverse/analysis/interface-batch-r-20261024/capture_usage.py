"""Bounded telemetry for the user's continuation; no message bodies exported."""
from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = "01a16e95-4388-7971-a513-452557fd8d16"
HOME = Path("D:/CodexHome/sessions/2026/10/24")
OUT = Path(__file__).resolve().parent
rootfile = next(HOME.glob("rollout-*" + ROOT + ".jsonl"))

def events(path):
    for line in path.open(encoding="utf-8"):
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue

baseline, baseline_utc, dispatch = {}, None, {}
previous = {}
for event in events(rootfile):
    value = event.get("payload", {})
    if value.get("type") == "token_count" and value.get("info"):
        previous = value["info"]["total_token_usage"]
    if value.get("type") == "message" and value.get("role") == "user" and any("继续保持三个agent" in part.get("text", "") for part in value.get("content", [])):
        baseline, baseline_utc = dict(previous), event.get("timestamp")
    if event.get("type") == "response_item" and value.get("type") == "function_call" and "spawn_agent" in value.get("name", ""):
        a = json.loads(value.get("arguments", "{}"))
        dispatch[a.get("task_name")] = {"utc": event.get("timestamp"), "fork_turns": a.get("fork_turns")}
assert baseline_utc, "Continuation user event not found"
lifecycle = []
for event in events(rootfile):
    value = event.get("payload", {})
    if event.get("timestamp", "") < baseline_utc:
        continue
    if event.get("type") == "response_item" and value.get("type") == "function_call" and any(t in value.get("name", "") for t in ("spawn_agent", "followup_task", "interrupt_agent")):
        a = json.loads(value.get("arguments", "{}"))
        lifecycle.append({"call_emitted_utc": event.get("timestamp"), "tool": value.get("name"), "target": a.get("target", a.get("task_name")), "fork_turns": a.get("fork_turns")})
rows = []
for path in list(HOME.glob("rollout-*.jsonl")) + list((HOME.parent / "25").glob("rollout-*.jsonl")):
    if path.stat().st_mtime < rootfile.stat().st_ctime and ROOT not in path.name:
        continue
    iterator = events(path)
    first = next(iterator, {})
    if first.get("type") != "session_meta":
        continue
    meta = first["payload"]
    isroot = meta.get("id") == ROOT
    if not isroot and (meta.get("parent_thread_id") != ROOT or meta.get("timestamp", "") < baseline_utc):
        continue
    usage, last, completed, completions = {}, None, None, []
    for event in iterator:
        value = event.get("payload", {})
        if value.get("type") == "token_count" and value.get("info"):
            usage, last = value["info"]["total_token_usage"], event.get("timestamp")
        if value.get("type") == "task_complete" and event.get("timestamp", "") >= baseline_utc:
            completed = event.get("timestamp")
            completions.append(completed)
    if isroot:
        usage = {k: v - baseline.get(k, 0) for k, v in usage.items()}
    else:
        usage = dict(usage)
    usage["uncached_input_tokens"] = usage.get("input_tokens", 0) - usage.get("cached_input_tokens", 0)
    name = (meta.get("agent_path") or "/root").rsplit("/", 1)[-1]
    rows.append({"name": name, "id": meta.get("id"), "created_utc": meta.get("timestamp"), "dispatch": dispatch.get(name), "last_telemetry_utc": last, "task_complete_event_utc": completed, "all_task_complete_events_utc": completions, "usage": usage, "source": str(path)})
keys = ("input_tokens", "cached_input_tokens", "uncached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")
r = {"batch": "R", "snapshot_utc": datetime.now(timezone.utc).isoformat(), "start_user_event_utc": baseline_utc, "root_usage_baseline": baseline, "lifecycle_calls": lifecycle, "correction_handoff_note": "One ordering error: author followup emitted 16:09:30.825, reviewer interrupt emitted 16:09:41.533, approximately 10.708 seconds with four running children; then three restored. Reviewer resumed 16:10:46.773 after author completed. These are call emission times, not measured effective work boundaries.", "sessions": rows, "total": {k: sum(row["usage"].get(k, 0) for row in rows) for k in keys}, "limitations": ["Cached input is included in input; reasoning is included in output. Neither is added twice.", "Root is the delta since the token event preceding the continuation user instruction. Only new children of this root are included.", "Snapshot excludes subsequent output and invisible internal tool/approval usage; not billing data.", "No close/release tool exists; completed does not establish released threads."]}
(OUT / "usage-snapshot.json").write_text(json.dumps(r, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"start": baseline_utc, "snapshot": r["snapshot_utc"], "names": [row["name"] for row in rows], "total": r["total"]}, ensure_ascii=False))
