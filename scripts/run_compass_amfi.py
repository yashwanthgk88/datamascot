"""Refresh DataMascot NAV tables from official AMFI via the guarded database RPC."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

def main():
    origin = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    parsed = urllib.parse.urlparse(origin)
    if parsed.scheme != "https" or not parsed.hostname or not parsed.hostname.endswith(".supabase.co") or parsed.path or parsed.username or parsed.password or not key:
        raise SystemExit("A Supabase project origin and server-side collector secret are required.")
    request = urllib.request.Request(
        origin + "/rest/v1/rpc/refresh_compass_amfi_navs",
        data=b"{}",
        headers={"apikey": key, "Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        raise SystemExit("Collector RPC rejected the request (HTTP " + str(error.code) + "). Check server-side grants and secrets.") from None
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise SystemExit("Collector connection failed; no success is claimed.") from None
    if not isinstance(result, dict) or result.get("ok") is not True:
        raise SystemExit("AMFI import failed validation. Review private scraper_runs for the source error.")
    print(json.dumps({key: result.get(key) for key in ("ok", "source", "updated", "run_id")}))
    if not isinstance(result.get("updated"), int) or result["updated"] < 100:
        raise SystemExit("Unexpectedly small refresh; verify source coverage.")

if __name__ == "__main__":
    main()
