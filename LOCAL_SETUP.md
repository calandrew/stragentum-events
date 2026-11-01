# Running the Event Scout locally (Claude desktop app, Code tab)

Why: some sources (Auckland Business Chamber, ExportNZ) return 403 to cloud IPs. A local run uses your own IP and may load them. Untested until step 3 passes.

## 1. One-time setup
1. Install Git, and connect GitHub in the Claude desktop app (Settings).
2. In a terminal:
   ```
   git clone https://github.com/calandrew/stragentum-events.git
   cd stragentum-events
   git checkout claude/event-feed
   ```
3. Open the Code tab in the desktop app, start a LOCAL session in that folder.

## 2. Test the blocked sources
Paste into the local session:
> Fetch https://aucklandchamber.co.nz/events/ and https://exportnz.org.nz/home/auckland and list upcoming events. Report the HTTP result for each.

- Both load: continue to step 3.
- Still 403: local will not fix those sites. Keep the cloud routine and paste those pages in manually.

## 3. Run prompt (use for manual runs and the schedule)
> You are the Stragentum Event Scout. Run "git fetch origin" then "git checkout -B claude/event-feed origin/claude/event-feed". Read SPEC.md and follow it exactly: research Auckland business events from today to today + 42 days across every source tier, score them, write shortlisted events to new.json. Run: python3 scout.py merge --repo . --new new.json (use "python" if python3 is missing). Delete new.json. Commit calendar.ics, events.json and any SPEC.md changes, then run "git push origin claude/event-feed". Push only to that branch; never open a PR or push elsewhere. Finish with the report in SPEC.md section 7, flagging sources that failed.

## 4. Schedule it
In the desktop app, create a scheduled task using the prompt above, in this folder, fortnightly (cloud routine ran roughly fortnightly). Local scheduled tasks only fire while the computer is on and the app is open. If a run is missed, run it manually when you next open the app, or enable any "run missed task when app opens" option your version offers.

## 5. Avoid duplicates
Pause the cloud routine at claude.ai/code/routines once the local one works.

## Notes
- Needs Python 3 on the PC for scout.py.
- Only edit and push the claude/event-feed branch.
