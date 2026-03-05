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
    print(f"[BACKFILL] {team_id}/{channel_id}")
    url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages"
    out = BASE_DIR / "backfill" / f"team_{team_id}" / f"channel_{channel_id}.jsonl"

    msg_count = 0
    while url:
        data = graph_get(url)
        for msg in data.get("value", []):
            append_jsonl(out, msg)
            msg_count += 1
        url = data.get("@odata.nextLink")
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