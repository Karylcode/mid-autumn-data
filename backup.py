import os
import json
import datetime
import urllib.request

BASE_DIR = os.path.dirname(__file__)
SAVE_DIR = os.path.join(BASE_DIR, 'backups')
DEFAULT_URL = 'https://mid-autumn-backend.onrender.com/api/leaderboard'

def fetch_leaderboard(url: str = None):
    url = url or os.environ.get('LEADERBOARD_URL', DEFAULT_URL)
    os.makedirs(SAVE_DIR, exist_ok=True)
    resp = urllib.request.urlopen(url, timeout=15)
    raw = resp.read().decode('utf-8')
    return json.loads(raw)

def perform_backup(data: dict):
    ts = datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    fname = f'leaderboard-{ts}.json'
    path = os.path.join(SAVE_DIR, fname)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    latest_path = os.path.join(SAVE_DIR, 'latest.json')
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    manifest_path = os.path.join(SAVE_DIR, 'manifest.json')
    manifest = []
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as mf:
                manifest = json.load(mf)
        except Exception:
            manifest = []

    count = len(data.get('items', []))
    entry = {'timestamp': ts, 'file': fname, 'count': count}
    manifest.append(entry)
    with open(manifest_path, 'w', encoding='utf-8') as mf:
        json.dump(manifest, mf, ensure_ascii=False, indent=2)
    return entry

if __name__ == '__main__':
    data = fetch_leaderboard()
    entry = perform_backup(data)
    print(f"Saved {entry['file']} with {entry['count']} items.")