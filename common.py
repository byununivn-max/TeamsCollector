import os, time, json, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
BASE_DIR = Path(os.getenv("BASE_DIR", "./data"))

TOKEN_CACHE = {"access_token": None, "expires_at": 0}

def get_token():
    now = time.time()
    if TOKEN_CACHE["access_token"] and TOKEN_CACHE["expires_at"] - now > 60:
        return TOKEN_CACHE["access_token"]
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }
    resp = requests.post(url, data=data)
    if resp.status_code != 200:
        print("Token error:", resp.status_code, resp.text)
        resp.raise_for_status()
    body = resp.json()
    TOKEN_CACHE["access_token"] = body["access_token"]
    TOKEN_CACHE["expires_at"] = now + body.get("expires_in", 3600)
    return TOKEN_CACHE["access_token"]

def graph_get(url):
    import requests.exceptions
    for attempt in range(5):
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.get(url, headers=headers, timeout=60)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
            print(f"Network error: {e}. Retry {attempt+1}/5 in {2 ** attempt}s...")
            time.sleep(2 ** attempt)
            continue
            
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", "5"))
            print(f"429 Too Many Requests. Sleeping {wait} seconds...")
            time.sleep(wait)
            continue
        if 500 <= resp.status_code < 600:
            print(f"5xx error {resp.status_code}. Retry {attempt+1}/5 in {2 ** attempt}s...")
            time.sleep(2 ** attempt)
            continue
        if resp.status_code != 200:
            print("Graph error:", resp.status_code, resp.text)
            resp.raise_for_status()
        return resp.json()
    raise RuntimeError("graph_get: repeated failures")

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def append_jsonl(path: Path, obj: dict):
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")