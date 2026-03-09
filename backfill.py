from common import BASE_DIR, graph_get, append_jsonl

def get_all_teams():
    teams = []
    url = "https://graph.microsoft.com/v1.0/teams"
    while url:
        data = graph_get(url)
        teams.extend(data.get("value", []))
        url = data.get("@odata.nextLink")
    return teams

def get_channels(team_id):
    url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels"
    return graph_get(url).get("value", [])

def backfill_channel(team_id, channel_id):
    out_final = BASE_DIR / "backfill" / f"team_{team_id}" / f"channel_{channel_id}.jsonl"
    out_tmp = BASE_DIR / "backfill" / f"team_{team_id}" / f"channel_{channel_id}.tmp.jsonl"
    
    # [Resume Logic] 정상적으로 100% 완료된 파일만 건너뜁니다.
    if out_final.exists():
        print(f"[SKIP] {team_id}/{channel_id} already exists (fully collected).")
        return
        
    # 만약 중간에 멈춰서 생긴 임시 파일이 있다면, 처음부터 다시 받기 위해 삭제합니다.
    if out_tmp.exists():
        out_tmp.unlink()
        
    print(f"[BACKFILL] {team_id}/{channel_id}")
    url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages"

    msg_count = 0
    while url:
        data = graph_get(url)
        for msg in data.get("value", []):
            msg_id = msg.get("id")
            
            # Fetch replies for this message
            if msg_id:
                replies_url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages/{msg_id}/replies"
                replies = []
                while replies_url:
                    replies_data = graph_get(replies_url)
                    replies.extend(replies_data.get("value", []))
                    replies_url = replies_data.get("@odata.nextLink")
                    
                msg["replies"] = replies
            
            append_jsonl(out_tmp, msg)
            msg_count += 1
        url = data.get("@odata.nextLink")
        
    # 수집이 100% 완료되면 임시 파일을 최종 파일명으로 변경하여 '완료 마킹' 합니다.
    if out_tmp.exists():
        out_tmp.rename(out_final)
        
    print(f"[DONE] {team_id}/{channel_id} msgs={msg_count}")

def main():
    teams = get_all_teams()
    print(f"Teams={len(teams)}")
    for t in teams:
        team_id = t["id"]
        print(f"\n== Team {team_id} ==")
        channels = get_channels(team_id)
        for ch in channels:
            backfill_channel(team_id, ch["id"])

if __name__ == "__main__":
    main()