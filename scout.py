#!/usr/bin/env python3
"""Stragentum Event Scout: merge researched events into a subscribed Outlook feed.

State lives in a public GitHub repo:
  calendar.ics  - the feed Outlook subscribes to (raw URL)
  events.json   - canonical event store (source of truth for the .ics)
  SPEC.md / scout.py - the research spec and this script

Usage:
  scout.py merge --repo <clone dir> --new new.json   -> then git commit + push
  scout.py render --events events.json --out calendar.ics
"""
import argparse, hashlib, json, re, sys
from datetime import datetime, date, timedelta, timezone
from pathlib import Path

CAL_NAME = "Stragentum Prospect Events"
TZID = "Pacific/Auckland"
CATEGORY = "Stragentum: Prospect Event"
KEEP_PAST_DAYS = 14

VTIMEZONE = """BEGIN:VTIMEZONE
TZID:Pacific/Auckland
BEGIN:STANDARD
DTSTART:19700405T030000
RRULE:FREQ=YEARLY;BYMONTH=4;BYDAY=1SU
TZOFFSETFROM:+1300
TZOFFSETTO:+1200
TZNAME:NZST
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19700927T020000
RRULE:FREQ=YEARLY;BYMONTH=9;BYDAY=-1SU
TZOFFSETFROM:+1200
TZOFFSETTO:+1300
TZNAME:NZDT
END:DAYLIGHT
END:VTIMEZONE"""

REQUIRED = ["title", "start", "url"]


# ---------- helpers ----------
def uid_for(ev):
    key = re.sub(r"[^a-z0-9]", "", ev["title"].lower())[:60] + ev["start"][:10]
    return hashlib.sha1(key.encode()).hexdigest()[:16] + "@stragentum-scout"


def esc(s):
    return (str(s).replace("\\", "\\\\").replace(";", "\\;")
            .replace(",", "\\,").replace("\r", "").replace("\n", "\\n"))


def fold(line):
    b = line.encode("utf-8")
    if len(b) <= 75:
        return line
    out, cur = [], b""
    for ch in line:
        cb = ch.encode("utf-8")
        limit = 75 if not out else 74
        if len(cur) + len(cb) > limit:
            out.append(cur.decode("utf-8"))
            cur = b""
        cur += cb
    out.append(cur.decode("utf-8"))
    return "\r\n ".join(out)


def parse_local(s):
    """'2026-10-14T17:30' or '2026-10-14' -> (datetime|date, is_all_day)."""
    if "T" in s:
        return datetime.fromisoformat(s[:16]), False
    return date.fromisoformat(s[:10]), True


def html(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------- rendering ----------
def description(ev):
    lines = [f"BOOK / REGISTER: {ev['url']}", ""]
    fields = [
        ("Fit", f"{ev.get('fit_score', '?')}/5. {ev.get('fit_rationale', '')}".strip()),
        ("Organiser", ev.get("organiser")),
        ("Time", ev.get("time_text")),
        ("Venue", ", ".join(x for x in [ev.get("venue"), ev.get("address")] if x)),
        ("Cost", ev.get("cost")),
        ("Registration", ev.get("registration")),
        ("Audience", ev.get("audience")),
        ("Networking", ev.get("networking")),
        ("Speakers", ev.get("speakers")),
        ("Agenda", ev.get("agenda")),
        ("Unverified", ev.get("unverified")),
        ("Source", ev.get("source_url")),
    ]
    for k, v in fields:
        if v:
            lines.append(f"{k}: {v}")
    lines += ["", f"Status: UNCONFIRMED prospect. Found {ev.get('first_seen', '')}, "
              f"last checked {ev.get('last_seen', '')}."]
    return "\n".join(lines)


def alt_desc(ev):
    body = html(description(ev)).replace("\n", "<br>")
    link = f'<p><b><a href="{html(ev["url"])}">Book / register</a></b></p>'
    return f"<html><body>{link}{body}</body></html>"


def vevent(ev, stamp):
    start, all_day = parse_local(ev["start"])
    if all_day:
        end = date.fromisoformat(ev["end"][:10]) + timedelta(days=1) if ev.get("end") else start + timedelta(days=1)
        dt = [f"DTSTART;VALUE=DATE:{start:%Y%m%d}", f"DTEND;VALUE=DATE:{end:%Y%m%d}"]
    else:
        end = parse_local(ev["end"])[0] if ev.get("end") and "T" in ev["end"] else start + timedelta(hours=2)
        dt = [f"DTSTART;TZID={TZID}:{start:%Y%m%dT%H%M%S}", f"DTEND;TZID={TZID}:{end:%Y%m%dT%H%M%S}"]
    prefix = "[?] " if ev.get("fit_score", 3) < 4 else ""
    loc = ", ".join(x for x in [ev.get("venue"), ev.get("address")] if x) or "Auckland (venue TBC)"
    props = ["BEGIN:VEVENT", f"UID:{ev['uid']}", f"DTSTAMP:{stamp}", f"SEQUENCE:{ev.get('sequence', 0)}",
             *dt,
             f"SUMMARY:{esc(prefix + ev['title'])}",
             f"LOCATION:{esc(loc)}",
             f"DESCRIPTION:{esc(description(ev))}",
             f"X-ALT-DESC;FMTTYPE=text/html:{esc(alt_desc(ev))}",
             f"URL:{ev['url']}",
             f"CATEGORIES:{esc(CATEGORY)}",
             "STATUS:TENTATIVE", "TRANSP:TRANSPARENT",
             "X-MICROSOFT-CDO-BUSYSTATUS:FREE", "X-MICROSOFT-CDO-INTENDEDSTATUS:FREE",
             "CLASS:PUBLIC", "END:VEVENT"]
    return [fold(p) for p in props]


def render(events):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Stragentum//Event Scout//EN",
           "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
           f"X-WR-CALNAME:{CAL_NAME}", f"X-WR-TIMEZONE:{TZID}",
           "REFRESH-INTERVAL;VALUE=DURATION:PT12H", "X-PUBLISHED-TTL:PT12H",
           *VTIMEZONE.splitlines()]
    for ev in sorted(events, key=lambda e: e["start"]):
        out += vevent(ev, stamp)
    out.append("END:VCALENDAR")
    return "\r\n".join(out) + "\r\n"


# ---------- merge ----------
def merge(existing, new, today):
    store = {e["uid"]: e for e in existing}
    added, updated = [], []
    for ev in new:
        missing = [k for k in REQUIRED if not ev.get(k)]
        if missing:
            print(f"SKIP (missing {missing}): {ev.get('title')}", file=sys.stderr)
            continue
        ev["uid"] = ev.get("uid") or uid_for(ev)
        ev["last_seen"] = today.isoformat()
        if ev["uid"] in store:
            old = store[ev["uid"]]
            ev["first_seen"] = old.get("first_seen", today.isoformat())
            changed = any(old.get(k) != ev.get(k) for k in ("start", "end", "venue", "address", "cost", "url"))
            ev["sequence"] = old.get("sequence", 0) + (1 if changed else 0)
            (updated if changed else []).append(ev["title"])
            store[ev["uid"]] = {**old, **{k: v for k, v in ev.items() if v not in (None, "")}}
        else:
            ev["first_seen"] = today.isoformat()
            ev["sequence"] = 0
            store[ev["uid"]] = ev
            added.append(ev["title"])
    cutoff = today - timedelta(days=KEEP_PAST_DAYS)
    kept = [e for e in store.values() if date.fromisoformat((e.get("end") or e["start"])[:10]) >= cutoff]
    pruned = len(store) - len(kept)
    return kept, added, updated, pruned


# ---------- repo mode ----------
def main():
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["merge", "render"])
    p.add_argument("--repo", default=".", help="local clone of the feed repo")
    p.add_argument("--new"); p.add_argument("--events"); p.add_argument("--out")
    a = p.parse_args()
    today = datetime.now(timezone(timedelta(hours=12))).date()

    if a.cmd == "render":
        evs = json.loads(Path(a.events).read_text())
        Path(a.out).write_text(render(evs), newline="")
        print(f"wrote {a.out} ({len(evs)} events)")
        return

    repo = Path(a.repo)
    store = repo / "events.json"
    existing = json.loads(store.read_text()) if store.exists() else []
    new = json.loads(Path(a.new).read_text())
    kept, added, updated, pruned = merge(existing, new, today)
    store.write_text(json.dumps(sorted(kept, key=lambda e: e["start"]), indent=1, ensure_ascii=False))
    (repo / "calendar.ics").write_text(render(kept), newline="")
    print(json.dumps({"added": added, "updated": updated, "pruned": pruned,
                      "total_in_feed": len(kept)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
