from datetime import datetime, timezone
from common import BASE_DIR, graph_get, append_jsonl
from sync_state import get_state, upsert_state
from backfill import get_all_teams, get_channels

def sync_channel(team, channel):
    delta, last = get_state(team, channel)
    if delta:
        url = delta
        print(f"[DELTA] reuse {team}/{channel}")
    else:
        url = f"https://graph.microsoft.com/v1.0/teams/{team}/channels/{channel}/messages/delta"
        print(f"[DELTA] first {team}/{channel}")

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    out = BASE_DIR / "incremental" / f"team_{team}" / f"channel_{channel}_{today}.jsonl"

    total = 0
    new_delta = None

    while url:
        data = graph_get(url)
        for msg in data.get("value", []):
            append_jsonl(out, msg)
            total += 1
        new_delta = data.get("@odata.deltaLink") or new_delta
        url = data.get("@odata.nextLink")

    ts = datetime.now(timezone.utc).isoformat()
    if new_delta:
        upsert_state(team, channel, new_delta, ts)

    print(f"[DONE] {team}/{channel} msgs={total}")

def main():
    teams = get_all_teams()
    for t in teams:
        channels = get_channels(t["id"])
        for ch in channels:
            sync_channel(t["id"], ch["id"])

if __name__ == "__main__":
    main()