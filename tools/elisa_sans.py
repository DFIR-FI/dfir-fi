#!/usr/bin/env python3
"""Import Elisa's SANS forensics (FOR*) course sessions into content/training.

Elisa lists SANS courses at https://yrityksille.elisa.fi/kurssit. Session
dates only appear as free text on each course page, e.g.
"Koulutus järjestetään 21.–26.9.2026", and only the next session is shown,
so every session we see is saved as its own file and kept once it is past.

Rules:
  - New session            -> create content/training/elisa-<code>-<start>.md
  - Existing session       -> leave untouched
  - Future session no longer shown on its (successfully fetched) course page
                           -> delete it (rescheduled or cancelled)
  - Past sessions          -> never touched
  - Anything unrecognised (date text we can't parse, no FOR courses found,
    network errors)        -> exit non-zero without changing anything

Usage:
  tools/elisa_sans.py              update content/training from the live site
  tools/elisa_sans.py --dry-run    only print what would change
  tools/elisa_sans.py --wayback    one-time backfill from Internet Archive
                                   snapshots (never deletes anything)
"""

import argparse
import datetime as dt
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = "https://yrityksille.elisa.fi"
LISTING_URL = BASE + "/kurssit"
COURSE_PATH_RE = re.compile(r"/kurssit/sans-(for\d{3})\b", re.I)
USER_AGENT = "dfir.fi training importer (+https://dfir.fi/training/)"
REQUEST_PAUSE_S = 2
TRAINING_DIR = Path(__file__).resolve().parent.parent / "content" / "training"
HELSINKI = ZoneInfo("Europe/Helsinki")

DASH = r"\s*[-–—]\s*"
# Order matters: the most specific forms first.
DATE_PATTERNS = [
    # 30.12.2026–2.1.2027
    re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})" + DASH + r"(\d{1,2})\.(\d{1,2})\.(\d{4})"),
    # 30.9.–5.10.2026
    re.compile(r"(\d{1,2})\.(\d{1,2})\." + DASH + r"(\d{1,2})\.(\d{1,2})\.(\d{4})"),
    # 21.–26.9.2026
    re.compile(r"(\d{1,2})\." + DASH + r"(\d{1,2})\.(\d{1,2})\.(\d{4})"),
    # 21.9.2026
    re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})"),
]
SESSION_MARKER = "järjestetään"


class ImportError_(Exception):
    """Something we don't recognise; abort without changing files."""


# --- fetching -------------------------------------------------------------

def fetch(url, retries=4):
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < retries - 1:
                time.sleep(15 * (attempt + 1))
                continue
            raise ImportError_(f"HTTP {e.code} for {url}") from e
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(10)
                continue
            raise ImportError_(f"cannot fetch {url}: {e.reason}") from e
    raise ImportError_(f"cannot fetch {url}")


# --- parsing --------------------------------------------------------------

def page_text(page):
    """Visible text, with tags turned into ' | ' separators."""
    page = re.sub(r"<(script|style)\b.*?</\1>", " ", page, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " | ", page)
    text = html.unescape(text).replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return re.sub(r"(\s*\|\s*)+", " | ", text)


def parse_dates(fragment):
    """Parse one session date expression -> (start, end) dates."""
    for i, pat in enumerate(DATE_PATTERNS):
        m = pat.match(fragment)
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        try:
            if i == 0:
                start, end = dt.date(g[2], g[1], g[0]), dt.date(g[5], g[4], g[3])
            elif i == 1:
                start, end = dt.date(g[4], g[1], g[0]), dt.date(g[4], g[3], g[2])
            elif i == 2:
                start, end = dt.date(g[3], g[2], g[0]), dt.date(g[3], g[2], g[1])
            else:
                start = end = dt.date(g[2], g[1], g[0])
        except ValueError as e:
            raise ImportError_(f"invalid session date {fragment[:40]!r}: {e}") from e
        if end < start or (end - start).days > 31:
            raise ImportError_(f"implausible date range: {fragment[:40]!r}")
        return start, end
    raise ImportError_(f"unrecognised session date: {fragment[:60]!r}")


def parse_sessions(text):
    """All sessions announced with 'järjestetään <dates>' in the page text."""
    sessions = set()
    for m in re.finditer(SESSION_MARKER, text, flags=re.I):
        fragment = text[m.end():].lstrip(" |")
        # "järjestetään etänä" etc. is not a date; a date we can't parse is an error
        if fragment[:1].isdigit():
            sessions.add(parse_dates(fragment))
    return sorted(sessions)


def parse_fact(text, label):
    m = re.search(label + r":\s*\|?\s*([^|]+)", text)
    return m.group(1).strip().rstrip(".") if m else ""


def parse_course_page(page):
    text = page_text(page)
    if "Elisa" not in text:
        raise ImportError_("course page does not look like an Elisa page")
    desc = ""
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', page)
    if m:
        desc = html.unescape(m.group(1)).strip()
    return {
        "sessions": parse_sessions(text),
        "price": parse_fact(text, "Hinta"),
        "place": parse_fact(text, "Paikka"),
        "description": desc,
    }


def parse_listing(page):
    """FOR course codes on the listing, with their short description."""
    codes = sorted({c.lower() for c in COURSE_PATH_RE.findall(page)})
    if not codes:
        raise ImportError_("no SANS FOR courses found on the listing page")
    courses = {}
    for code in codes:
        block = re.search(r'<div id="SANS ' + code.upper() + r'".*?(?=<div id="SANS |\Z)', page, re.S)
        desc = cert = ""
        if block:
            b = block.group(0)
            paras = [page_text(p).strip(" |") for p in re.findall(r"<p>(.*?)</p>", b, re.S)]
            paras = [p for p in paras if p and not p.startswith(("Tutustu", "Kesto", "Ajankohta", "Hinta"))]
            if paras:
                desc = paras[0]
            cm = re.search(r"suorittaa (.+?) -sertifikaat", page_text(b))
            if cm:
                cert = cm.group(1).strip()
        courses[code] = {"description": desc, "cert": cert}
    return courses


# --- session files ----------------------------------------------------------

def session_path(code, start):
    return TRAINING_DIR / f"elisa-{code}-{start.isoformat()}.md"


def yaml_str(s):
    return json.dumps(s, ensure_ascii=False)


def render_session(code, start, end, info, first_seen):
    body = info.get("description") or f"SANS {code.upper()} course organised by Elisa in Finland."
    title = "SANS " + code.upper()
    cert = re.search(r"\((G[A-Z0-9]{2,6})\)", info.get("cert", ""))
    if cert:
        title += f" ({cert.group(1)})"  # e.g. "SANS FOR508 (GCFA)"
    place = info.get("place") or "Helsinki"
    return "\n".join([
        "---",
        f"title: {yaml_str(title)}",
        'provider: "Elisa"',
        f"date: {first_seen.isoformat()}",
        "draft: false",
        f"coursedate: {start.isoformat()}",
        f"courseend: {end.isoformat()}",
        f"pricing: {yaml_str(info.get('price') or 'Check website')}",
        f"courselink: {yaml_str(BASE + '/kurssit/sans-' + code)}",
        'language: "English"',
        f"location: {yaml_str(place)}",
        "source: elisa",
        "---",
        "",
        body,
        "",
    ])


def existing_sessions():
    """{(code, start): path} for files this importer owns."""
    found = {}
    for path in TRAINING_DIR.glob("elisa-for*-*.md"):
        text = path.read_text(encoding="utf-8")
        if "\nsource: elisa\n" not in text:
            continue
        m = re.match(r"elisa-(for\d{3})-(\d{4}-\d{2}-\d{2})\.md$", path.name)
        if m:
            found[(m.group(1), dt.date.fromisoformat(m.group(2)))] = path
    return found


# --- modes ------------------------------------------------------------------

def plan_live(today):
    """Return (creates, deletes) from the live site."""
    listing = parse_listing(fetch(LISTING_URL))
    have = existing_sessions()
    creates, deletes = [], []
    for code, meta in listing.items():
        time.sleep(REQUEST_PAUSE_S)
        course = parse_course_page(fetch(f"{BASE}/kurssit/sans-{code}"))
        info = {**meta, **{k: v for k, v in course.items() if v and k != "description"}}
        if not info.get("description"):
            info["description"] = course["description"]
        shown = set()
        for start, end in course["sessions"]:
            shown.add(start)
            if (code, start) not in have:
                creates.append((session_path(code, start), render_session(code, start, end, info, today)))
        for (c, start), path in have.items():
            if c == code and start > today and start not in shown:
                deletes.append(path)
    return creates, deletes


def plan_wayback(today):
    """Return (creates, []) from Internet Archive snapshots of the FOR pages."""
    cdx = fetch("https://web.archive.org/cdx/search/cdx?url=yrityksille.elisa.fi/kurssit/sans-for*"
                "&output=json&fl=timestamp,original&filter=statuscode:200&collapse=digest")
    rows = json.loads(cdx)[1:]
    have = existing_sessions()
    try:
        listing = parse_listing(fetch(LISTING_URL))
    except ImportError_:
        listing = {}
    seen = {}  # (code, start) -> (end, first_seen, info)
    for ts, original in sorted(rows):
        m = COURSE_PATH_RE.search(original)
        if not m:
            continue
        code = m.group(1).lower()
        time.sleep(REQUEST_PAUSE_S)
        try:
            course = parse_course_page(fetch(f"https://web.archive.org/web/{ts}id_/{original}"))
        except ImportError_ as e:
            print(f"  skip snapshot {ts} {code}: {e}", file=sys.stderr)
            continue
        snap_day = dt.datetime.strptime(ts[:8], "%Y%m%d").date()
        info = {**listing.get(code, {}), **{k: v for k, v in course.items() if v and k != "description"}}
        if not info.get("description"):
            info["description"] = course["description"]
        for start, end in course["sessions"]:
            if (code, start) not in seen:
                seen[(code, start)] = (end, min(snap_day, today), info)
    creates = [
        (session_path(code, start), render_session(code, start, end, info, first_seen))
        for (code, start), (end, first_seen, info) in sorted(seen.items())
        if (code, start) not in have
    ]
    return creates, []


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="print changes, write nothing")
    ap.add_argument("--wayback", action="store_true", help="one-time backfill from the Internet Archive")
    args = ap.parse_args()

    today = dt.datetime.now(HELSINKI).date()
    try:
        creates, deletes = plan_wayback(today) if args.wayback else plan_live(today)
    except ImportError_ as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    for path, _ in creates:
        print(f"create {path.relative_to(TRAINING_DIR.parent.parent)}")
    for path in deletes:
        print(f"delete {path.relative_to(TRAINING_DIR.parent.parent)}")
    if not creates and not deletes:
        print("no changes")
    if args.dry_run:
        return 0
    for path, content in creates:
        path.write_text(content, encoding="utf-8")
    for path in deletes:
        path.unlink()
    return 0


if __name__ == "__main__":
    sys.exit(main())
