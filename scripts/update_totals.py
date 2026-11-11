"""Read this year's totals from the two Movember pages and write data/totals.json.

Only rewrites the file when a total changes, so the workflow only commits
(and GitHub Pages only redeploys) when there's actually new money.
Stops updating once voting closes, so the result is frozen at 11:59 pm on 30 November.
"""
import html, json, os, re, sys, urllib.request
from datetime import datetime, timezone, timedelta

PAGES = {
    "grow": "https://nz.movember.com/mospace/9417737",   # Grow the Mo (movember.com/m/nicktayls)
    "mow": "https://nz.movember.com/mospace/14257431",   # Mow the Mo
}
CLOSES = datetime(2026, 11, 30, 23, 59, 59, tzinfo=timezone(timedelta(hours=13)))
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "totals.json")
DEBUG_DIR = os.path.join(os.path.dirname(__file__), "..", "debug")

MONEY = r"\$\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)"
# Keys a page's embedded JSON might use for the current campaign's total.
JSON_KEYS = ("amountRaised", "raisedAmount", "totalRaised", "amount_raised", "raised", "donationTotal", "totalDonations")


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (GreatMoShowdown scoreboard; runs every 30 min)",
        "Accept-Language": "en-NZ,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def to_number(s):
    return float(s.replace(",", ""))


def page_text(raw):
    raw = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", raw)
    text = html.unescape(re.sub(r"(?s)<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", text)


def parse_total(raw):
    # 1. Visible text: the page shows this year's amount, then "Target: $X".
    #    (The lifetime figure reads "raised $X since 20YY", so it's never directly before "Target".)
    m = re.search(MONEY + r"\s*Target\s*:?", page_text(raw), re.I)
    if m:
        return to_number(m.group(1)), "text"
    # 2. Embedded JSON state, if the page is rendered client-side.
    for key in JSON_KEYS:
        m = re.search(r'"%s"\s*:\s*"?\$?([0-9][0-9,]*(?:\.[0-9]+)?)' % key, raw)
        if m:
            return to_number(m.group(1)), "json:" + key
    return None, None


def main():
    now = datetime.now(timezone.utc)
    if now > CLOSES:
        print("Voting has closed; leaving the final totals as they are.")
        return 0

    try:
        current = json.load(open(OUT))
    except Exception:
        current = {"grow": 0, "mow": 0, "updated": ""}

    new, failed = dict(current), []
    for side, url in PAGES.items():
        try:
            raw = fetch(url)
        except Exception as e:
            print(f"{side}: could not load {url}: {e}")
            failed.append(side)
            continue
        total, how = parse_total(raw)
        if total is None:
            os.makedirs(DEBUG_DIR, exist_ok=True)
            open(os.path.join(DEBUG_DIR, f"{side}.html"), "w").write(raw)
            print(f"{side}: couldn't find the total on the page (saved debug/{side}.html)")
            failed.append(side)
            continue
        print(f"{side}: ${total:,.2f} (via {how})")
        new[side] = int(total) if total.is_integer() else total

    changed = (new["grow"], new["mow"]) != (current.get("grow"), current.get("mow"))
    if changed:
        new["updated"] = now.isoformat(timespec="seconds")
        with open(OUT, "w") as f:
            json.dump(new, f, indent=2)
            f.write("\n")
        print("Totals changed; data/totals.json updated.")
    else:
        print("No change.")

    # Fail the run (so GitHub emails you) only if neither page could be read.
    return 1 if len(failed) == len(PAGES) else 0


if __name__ == "__main__":
    sys.exit(main())
