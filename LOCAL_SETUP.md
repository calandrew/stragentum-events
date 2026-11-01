# Running the Event Scout locally (Claude desktop app, Code tab)

Why: some sources (Auckland Business Chamber, ExportNZ) return 403 to cloud fetches. A local run can reach them: ExportNZ through a plain fetch, the Chamber only through the app's built-in browser.

## 1. One-time setup
1. Install Git and Python 3, and connect GitHub in the Claude desktop app (Settings).
   ```
   winget install --id Git.Git -e
   winget install --id Python.Python.3.13 -e --scope user
   ```
2. In a terminal:
   ```
   git clone https://github.com/calandrew/stragentum-events.git
   cd stragentum-events
   git checkout claude/event-feed
   ```
3. Open the Code tab in the desktop app, start a LOCAL session in that folder.

## 2. Test the blocked sources
Paste into the local session:
> Fetch https://exportnz.org.nz/home/auckland, and open https://aucklandchamber.co.nz/events/ in the built-in browser. List upcoming events from each and report whether each loaded.

Result on 2026-11-02 from this PC:
- ExportNZ: plain fetch returns 200 (the page only listed past events that day).
- Auckland Chamber: plain fetch, the iCal feed and the events API all return 403 (bot protection, not an IP block). The built-in browser loads the page and its event list.

If the Chamber also fails in the built-in browser, keep the cloud routine and paste that page in manually.

## 3. Run prompt (use for manual runs and the schedule)
> You are the Stragentum Event Scout. Run "git fetch origin" then "git checkout -B claude/event-feed origin/claude/event-feed". Read SPEC.md and follow it exactly: research Auckland business events from today to today + 42 days across every source tier, score them, write shortlisted events to new.json. Local-run overrides to SPEC.md: read the Auckland Business Chamber from https://aucklandchamber.co.nz/events/ using the built-in browser (plain fetches get 403), and fetch ExportNZ directly from https://exportnz.org.nz/home/auckland. Run: python scout.py merge --repo . --new new.json (on Windows "python3" is a Microsoft Store stub; if "python" fails, use "py -3"). Delete new.json. Commit calendar.ics, events.json and any SPEC.md changes, then run "git push origin claude/event-feed". Push only to that branch; never open a PR or push elsewhere. Finish with the report in SPEC.md section 7, flagging sources that failed.

## 4. Schedule it
In the desktop app, create a scheduled task using the prompt above, in this folder, fortnightly (cloud routine ran roughly fortnightly). Local scheduled tasks only fire while the computer is on and the app is open. If a run is missed, run it manually when you next open the app, or enable any "run missed task when app opens" option your version offers.

## 5. Avoid duplicates
Pause the cloud routine at claude.ai/code/routines once the local one works.

## Notes
- scout.py needs Python 3 (standard library only). It reads and writes UTF-8 explicitly, so macrons survive on Windows.
- Only edit and push the claude/event-feed branch.
