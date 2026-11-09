import json
import os
import glob
import urllib.request

DAEMON_DIR = r"C:\Users\cochr\.gemini\antigravity\daemon"
files = glob.glob(os.path.join(DAEMON_DIR, "hub_*.json"))

for f in files:
    try:
        with open(f, "r") as jf:
            data = json.load(jf)
        port = data.get("httpPort")
        token = data.get("csrfToken")
        pid = data.get("pid")
        url = f"http://127.0.0.1:{port}"
        print(f"Testing hub file {os.path.basename(f)} (pid {pid}, port {port})...")
        
        req = urllib.request.Request(url, headers={"x-codeium-csrf-token": token})
        try:
            with urllib.request.urlopen(req, timeout=2) as resp:
                print(f"  SUCCESS! HTTP status {resp.status}")
        except urllib.error.HTTPError as e:
            print(f"  Daemon responded with HTTP {e.code} (it is alive!)")
        except Exception as e:
            print(f"  Offline/Error: {e}")
    except Exception as e:
        print(f"Error reading {f}: {e}")

