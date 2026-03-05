import os
import requests
from dotenv import load_dotenv

# 1) .env 로드
load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# 2) 환경 변수 기본 체크 (디버깅용)
def check_env():
    print("=== ENV CHECK ===")
    print("TENANT_ID set?:", bool(TENANT_ID))
    print("CLIENT_ID set?:", bool(CLIENT_ID))
    print("CLIENT_SECRET length:", len(CLIENT_SECRET) if CLIENT_SECRET else 0)
    print("=================\n")
    if not (TENANT_ID and CLIENT_ID and CLIENT_SECRET):
        raise RuntimeError(".env에 TENANT_ID / CLIENT_ID / CLIENT_SECRET 중 하나 이상이 비어 있습니다.")

def get_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }
    resp = requests.post(url, data=data)
    if resp.status_code != 200:
        print("Token error status:", resp.status_code)
        print("Token error body:", resp.text)
        resp.raise_for_status()
    return resp.json()["access_token"]

def get_teams(access_token):
    # /groups 필터 대신 /teams 사용
    url = "https://graph.microsoft.com/v1.0/teams"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print("get_teams status:", resp.status_code)
        print("get_teams body:", resp.text)
        resp.raise_for_status()
    return resp.json().get("value", [])

def get_channels(access_token, team_id):
    url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print("get_channels status:", resp.status_code)
        print("get_channels body:", resp.text)
        resp.raise_for_status()
    return resp.json().get("value", [])

def get_messages(access_token, team_id, channel_id):
    url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bearer {access_token}"}
    page = 0
    while url:
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print("get_messages status:", resp.status_code)
            print("get_messages body:", resp.text)
            resp.raise_for_status()
        data = resp.json()
        page += 1
        for msg in data.get("value", []):
            print(msg["id"], msg.get("createdDateTime"))
        url = data.get("@odata.nextLink")
    print(f"메시지 조회 완료 (총 페이지: {page})")

if __name__ == "__main__":
    check_env()
    token = get_token()
    print("토큰 발급 성공")

    teams = get_teams(token)
    print(f"Teams 개수: {len(teams)}")

    if not teams:
        print("Teams가 하나도 조회되지 않습니다.")
    else:
        first_team = teams[0]
        print("테스트 팀:", first_team.get("displayName"), first_team["id"])

        channels = get_channels(token, first_team["id"])
        print(f"채널 개수: {len(channels)}")

        if not channels:
            print("채널이 없는 팀입니다.")
        else:
            first_channel = channels[0]
            print("테스트 채널:", first_channel.get("displayName"), first_channel["id"])
            get_messages(token, first_team["id"], first_channel["id"])