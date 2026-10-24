"""Read only this batch's rollout telemetry; never execute a target or read message text."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = "01a16e95-4388-7971-a513-452557fd8d16"
SESSIONS = Path("D:/CodexHome/sessions/2026/10/24")
OUTPUT = Path(__file__).resolve().parent
IDS = [ROOT, "01a16e96-5f67-7803-894d-ce553c82c306", "01a16e96-881e-7e82-ba37-1a610fa47958", "01a16e96-ae4a-7613-bb94-bc078050b11f"]
WORK_TIMES = {
    "dock_control_review_01": ("2026-10-24T15:45:16Z", "2026-10-24T15:49:40Z", 264),
    "app_summary_review_01": ("2026-10-24T15:45:29Z", "2026-10-24T15:48:44Z", 195),
    "app_history_review_01": ("2026-10-24T15:45:38Z", "2026-10-24T15:49:04.656Z", 206.656),
}
rows, dispatch = [], {}
for sid in IDS:
    path = next(SESSIONS.glob("rollout-*" + sid + ".jsonl"))
    meta, usage, usage_at, completed_at = {}, {}, None, None
    for line in path.open(encoding="utf-8"):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue  # A concurrent writer may not have finished the last line.
        value = event.get("payload", {})
        if event.get("type") == "session_meta":
            meta = value
        if value.get("type") == "token_count" and value.get("info"):
            usage = value["info"]["total_token_usage"]
            usage_at = event.get("timestamp")
        if value.get("type") == "task_complete":
            completed_at = event.get("timestamp")
        if event.get("type") == "response_item" and value.get("type") == "function_call" and "spawn_agent" in value.get("name", ""):
            args = json.loads(value.get("arguments", "{}"))
            dispatch[args.get("task_name")] = {"utc": event.get("timestamp"), "fork_turns": args.get("fork_turns")}
    name = (meta.get("agent_path") or "/root").rsplit("/", 1)[-1]
    usage = dict(usage)
    usage["uncached_input_tokens"] = usage.get("input_tokens", 0) - usage.get("cached_input_tokens", 0)
    rows.append({"name": name, "session_id": sid, "created_utc": meta.get("timestamp"), "dispatch": dispatch.get(name), "reviewer_reported_work_start_end_wall_seconds": WORK_TIMES.get(name), "last_telemetry_utc": usage_at, "task_complete_event_utc": completed_at, "usage": usage, "source": str(path)})
keys = ("input_tokens", "cached_input_tokens", "uncached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")
result = {"batch": "Q", "snapshot_utc": datetime.now(timezone.utc).isoformat(), "root_session_created_utc": rows[0]["created_utc"], "management_clock_baseline_utc": "2026-10-24T15:44:36Z", "root_usage_baseline": "zero at new root session creation; includes initial reads before management clock baseline", "notes": ["Input includes cached input; cached input is not added again.", "Reasoning is included in output and is not added again.", "Snapshot excludes later integration/final output and invisible internal approval/tool usage; not billing data.", "Wall clock includes reads, tool waits and communication; effective work time not measured.", "No agent close/release tool exists; task_complete is not proof of thread release."], "sessions": rows, "total": {k: sum(x["usage"].get(k, 0) for x in rows) for k in keys}}
(OUTPUT / "usage-snapshot.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"snapshot_utc": result["snapshot_utc"], "total": result["total"], "completed_events": {x["name"]: x["task_complete_event_utc"] for x in rows}}, ensure_ascii=False))
