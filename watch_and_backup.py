import os
import time
import json
import hashlib
from backup import fetch_leaderboard, perform_backup, DEFAULT_URL

BASE_DIR = os.path.dirname(__file__)
STATE_PATH = os.path.join(BASE_DIR, 'backups', 'state.json')
URL = os.environ.get('LEADERBOARD_URL', DEFAULT_URL)
INTERVAL = int(os.environ.get('CHECK_INTERVAL', '60'))  # seconds

def fingerprint(items):
    # 以排序後的 JSON 作為指紋，避免順序造成誤判
    normalized = json.dumps(items, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def load_last_fp():
    if not os.path.exists(STATE_PATH):
        return None
    try:
        with open(STATE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f).get('fingerprint')
    except Exception:
        return None

def save_last_fp(fp):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, 'w', encoding='utf-8') as f:
        json.dump({'fingerprint': fp, 'updated_at': int(time.time())}, f, ensure_ascii=False, indent=2)

def main():
    print(f"Watcher started. URL={URL} interval={INTERVAL}s")
    last_fp = load_last_fp()
    while True:
        try:
            payload = fetch_leaderboard(URL)
            items = payload.get('items', [])
            fp = fingerprint(items)
            if fp != last_fp:
                entry = perform_backup(payload)
                save_last_fp(fp)
                last_fp = fp
                print(f"Change detected -> backup: {entry['file']} ({entry['count']} items)")
            else:
                print("No change.")
        except Exception as e:
            print("Watcher error:", e)
        time.sleep(INTERVAL)

if __name__ == '__main__':
    main()