from datetime import datetime, timezone
from requests.exceptions import HTTPError
from common import BASE_DIR, graph_get, append_jsonl
from sync_status import get_state, upsert_state
from backfill import get_all_teams, get_channels

def _fetch_delta(url):
    """delta 페이지를 순회하며 메시지 목록과 새 deltaLink를 반환.
       페이징 중 400 에러 발생 시 수집된 데이터까지만 반환."""
    msgs = []
    new_delta = None
    while url:
        try:
            data = graph_get(url)
        except HTTPError as e:
            if e.response is not None and e.response.status_code == 400:
                print(f"[WARN] 400 on delta page, returning {len(msgs)} msgs collected so far")
                break
            raise
        msgs.extend(data.get("value", []))
        new_delta = data.get("@odata.deltaLink") or new_delta
        url = data.get("@odata.nextLink")
    return msgs, new_delta

def sync_channel(team, channel):
    delta, last = get_state(team, channel)
    fresh_url = f"https://graph.microsoft.com/v1.0/teams/{team}/channels/{channel}/messages/delta"

    if delta:
        url = delta
        print(f"[DELTA] reuse {team}/{channel}")
    else:
        url = fresh_url
        print(f"[DELTA] first {team}/{channel}")

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    out = BASE_DIR / "incremental" / f"team_{team}" / f"channel_{channel}_{today}.jsonl"

    msgs, new_delta = _fetch_delta(url)
    # 저장된 deltaLink 만료 시 처음부터 재시도
    if not msgs and not new_delta and delta:
        print(f"[WARN] deltaLink expired, resync from scratch {team}/{channel}")
        msgs, new_delta = _fetch_delta(fresh_url)

    total = 0
    for msg in msgs:
        msg_id = msg.get("id")
        # 각 메시지의 댓글(replies)도 함께 수집
        if msg_id:
            replies_url = f"https://graph.microsoft.com/v1.0/teams/{team}/channels/{channel}/messages/{msg_id}/replies"
            replies = []
            while replies_url:
                replies_data = graph_get(replies_url)
                replies.extend(replies_data.get("value", []))
                replies_url = replies_data.get("@odata.nextLink")
            msg["replies"] = replies
        append_jsonl(out, msg)
        total += 1

    ts = datetime.now(timezone.utc).isoformat()
    if new_delta:
        upsert_state(team, channel, new_delta, ts)

    print(f"[DONE] {team}/{channel} msgs={total}")

def main():
    teams = get_all_teams()
    errors = []
    for t in teams:
        channels = get_channels(t["id"])
        for ch in channels:
            try:
                sync_channel(t["id"], ch["id"])
            except Exception as e:
                print(f"[ERROR] {t['id']}/{ch['id']}: {e}")
                errors.append((t["id"], ch["id"], str(e)))
    if errors:
        print(f"\n[SUMMARY] {len(errors)} channel(s) failed:")
        for tid, cid, err in errors:
            print(f"  {tid}/{cid}: {err}")

if __name__ == "__main__":
    main()